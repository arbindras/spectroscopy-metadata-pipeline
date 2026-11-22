from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import pytest

import run_batch
from curation.build import load_llm_batch, write_tables
from llm_curation import runner
from llm_curation.providers import Completion, CurationError, make_provider
from llm_curation.schema import DETAIL_KEYS, SPECTRAL_FIELDS, clean_result, output_schema
from pdf.jats_reader import read_paper


JATS = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
 <front>
  <journal-meta><journal-title-group><journal-title>Test Journal</journal-title></journal-title-group></journal-meta>
  <article-meta>
   <article-id pub-id-type="doi">10.1000/test.1</article-id>
   <title-group><article-title>FTIR of test films</article-title></title-group>
   <contrib-group><contrib contrib-type="author"><name><surname>Doe</surname></name></contrib></contrib-group>
   <pub-date><year>2020</year></pub-date>
   <abstract><p>We measured FTIR spectra.</p></abstract>
   <custom-meta-group><custom-meta><meta-name>Data Availability</meta-name><meta-value>Data on Zenodo.</meta-value></custom-meta></custom-meta-group>
  </article-meta>
 </front>
 <body>
  <sec><title>Methods</title><p>Spectra recorded on a Bruker Vertex 70 at 4 cm-1.</p></sec>
  <sec><title>Results</title><p>Bands at 1650 cm-1.</p>
   <fig><label>Figure 1</label><caption><p>FTIR spectra of films.</p></caption></fig></sec>
 </body>
 <back><ref-list><ref><mixed-citation>Ignored reference</mixed-citation></ref></ref-list>
  <ack><p>Thanks.</p></ack></back>
</article>
"""


def _fake_answer(record_id: str) -> dict:
    spectral = {name: None for name in SPECTRAL_FIELDS}
    spectral.update(
        modality="FTIR spectroscopy of test films",
        spectral_range_original_min=400.0,
        spectral_range_original_max=4000.0,
        spectral_range_original_unit="cm-1",
        num_spectral_channels=50.0,  # float on purpose: clean_result must coerce
        num_samples=2,
        num_spectra=2,
        num_spectral_values=100,
        spectral_target_relationship="amide band -> film chemistry",
        source_file="spectra.csv",
        confidence=0.9,
    )
    return {
        "record_id": record_id,
        "has_spectra": True,
        "no_spectra_reason": None,
        "spectral": spectral,
        "details": {key: "Not reported" for key in DETAIL_KEYS},
        "curator_notes": "",
    }


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.users: list[str] = []

    def complete(self, system, user, schema):
        self.users.append(user)
        record_id = user.split("# RECORD ", 1)[1].split()[0] if "# RECORD " in user else "unknown"
        return Completion(_fake_answer(record_id), "fake-model", 10, 20, "end_turn")


def test_jats_reader_extracts_front_body_captions_and_skips_references(tmp_path):
    path = tmp_path / "123.xml"
    path.write_text(JATS, encoding="utf-8")

    document = read_paper(path)
    text = "\n".join(page.text for page in document.pages)

    assert "TITLE: FTIR of test films" in text
    assert "DOI: 10.1000/test.1" in text
    assert "AUTHORS: Doe" in text
    assert "DATA AVAILABILITY: Data on Zenodo." in text
    assert "SECTION: Methods" in text and "Bruker Vertex 70" in text
    assert "Figure 1: FTIR spectra of films." in text
    assert "Ignored reference" not in text


def test_output_schema_is_strict_and_complete():
    schema = output_schema()

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    spectral = schema["properties"]["spectral"]
    assert set(spectral["required"]) == set(SPECTRAL_FIELDS)
    assert all("anyOf" in spec for spec in spectral["properties"].values())
    assert schema["properties"]["details"]["required"] == DETAIL_KEYS


def test_clean_result_drops_nulls_and_coerces_types():
    answer = _fake_answer("7")
    answer["spectral"]["num_spectra"] = "3"
    answer["spectral"]["sampling_interval"] = "bad"
    answer["details"][DETAIL_KEYS[0]] = ""

    result = clean_result(answer)

    assert result["spectral"]["num_spectral_channels"] == 50
    assert isinstance(result["spectral"]["num_spectral_channels"], int)
    assert result["spectral"]["num_spectra"] == 3
    assert "sampling_interval" not in result["spectral"]
    assert "wavelength_min_nm" not in result["spectral"]
    assert result["details"][DETAIL_KEYS[0]] == "None"


def test_make_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(CurationError, match="ANTHROPIC_API_KEY"):
        make_provider("anthropic")
    with pytest.raises(CurationError, match="OPENAI_API_KEY"):
        make_provider("openai")
    with pytest.raises(CurationError, match="Unknown provider"):
        make_provider("other")


def test_write_tables_from_llm_json_derives_nm_and_lists_no_spectra(tmp_path):
    curated = tmp_path / "llm_curation"
    curated.mkdir()
    (curated / "1.json").write_text(json.dumps(clean_result(_fake_answer("1"))), encoding="utf-8")
    (curated / "2.json").write_text(
        json.dumps({"record_id": "2", "has_spectra": False, "no_spectra_reason": "XRD only"}), encoding="utf-8"
    )

    spectral, details, no_spectra = load_llm_batch(curated)
    summary = write_tables("testbatch", spectral, details, tmp_path, no_spectra=no_spectra)

    table = pd.read_parquet(summary["files"]["testbatch_spectroscopy_metadata"])
    assert table["record_id"].tolist() == ["1"]
    assert table.loc[0, "wavelength_min_nm"] == pytest.approx(2500.0)
    assert table.loc[0, "wavelength_max_nm"] == pytest.approx(25000.0)
    assert pd.read_parquet(summary["files"]["testbatch_dataset_details"]).shape[0] == 1
    assert pd.read_csv(summary["files"]["testbatch_no_spectra"]).to_dict("records") == [
        {"record_id": 2, "reason": "XRD only"}
    ]


def test_run_batch_end_to_end_with_fake_provider(tmp_path, monkeypatch):
    datasets = tmp_path / "Datasets"
    folder = datasets / "123_Test_films"
    folder.mkdir(parents=True)
    wavenumbers = np.linspace(400, 4000, 50)
    pd.DataFrame({"wavenumber": wavenumbers, "film_a": np.sin(wavenumbers), "film_b": np.cos(wavenumbers)}).to_csv(
        folder / "spectra.csv", index=False
    )
    papers = tmp_path / "papers"
    papers.mkdir()
    (papers / "123.xml").write_text(JATS, encoding="utf-8")

    args = argparse.Namespace(
        datasets=str(datasets), papers=str(papers), metadata=str(tmp_path / "none.csv"),
        output_root=str(tmp_path / "output"), batch="testbatch",
    )
    config = run_batch.prepare_inputs(run_batch.make_config(args), "testbatch")
    config["llm"]["concurrency"] = 1

    run_batch.step_extract(config, force=False)
    assert (tmp_path / "output" / "testbatch" / "spectroscopy_metadata.parquet").exists()

    fake = FakeProvider()
    monkeypatch.setattr(runner, "make_provider", lambda *a, **k: fake)
    summary = runner.curate_batch(config)
    assert summary == {"curated": 1, "skipped": 0, "failed": {}}

    pack = (tmp_path / "output" / "testbatch" / "llm_packs" / "123.md").read_text(encoding="utf-8")
    assert "spectra.csv" in pack and "Bruker Vertex 70" in pack
    assert fake.users and "spectra.csv" in fake.users[0]

    # Resumable: a second run skips records that already have JSON.
    assert runner.curate_batch(config)["skipped"] == 1

    run_batch.step_build(config, "testbatch", "llm", tmp_path / "output")
    table = pd.read_parquet(tmp_path / "output" / "testbatch_spectroscopy_metadata.parquet")
    assert table["record_id"].tolist() == ["123"]
    assert table.loc[0, "num_spectra"] == 2
