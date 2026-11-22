"""Curated (paper + dataset reviewed) metadata per batch.

Each batch has two modules:

* ``<batch>_spectral``  - dict ``R``  of SPECTRAL_SCHEMA fields per record_id
* ``<batch>_details``   - dict ``R2`` of the 22 descriptive "dataset details"
  fields per record_id (keys listed in ``curation.build.DETAIL_COLUMNS``)

``build_curated_parquet.py`` turns them into
``<output>/<batch>_spectroscopy_metadata.parquet`` and
``<output>/<batch>_dataset_details.parquet``.
"""
