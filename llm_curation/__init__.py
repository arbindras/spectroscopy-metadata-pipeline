"""LLM curation stage: paper + dataset evidence -> curated per-record metadata.

This automates what ``curation/<batch>_spectral.py`` / ``<batch>_details.py``
hold for the hand-curated batches:

1. ``evidence_pack.build_pack`` collects, per record, the Zenodo metadata,
   the dataset file inventory, README text, previews of data files, the
   automated extraction results (``output/<batch>/*.parquet``) and the paper
   text (PDF or JATS XML).
2. ``runner.curate_batch`` sends each pack to Claude or OpenAI with the
   instructions in ``prompts.py`` and the JSON schema in ``schema.py`` and
   caches one ``<record_id>.json`` per record.
3. ``curation.build.write_tables`` turns the JSON records into
   ``<batch>_spectroscopy_metadata.parquet`` and
   ``<batch>_dataset_details.parquet``, exactly like the curated batches.
"""
