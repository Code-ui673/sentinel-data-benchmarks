CAPR SAMPLE SUBSET — README
============================
This folder contains a true random subset of the full CAPR synthetic dataset.

Patients:            500 (drawn without replacement from 15,000; selection seed 20261006)
Linked tables:       limbs (690 rows), prostheses (690 rows),
                     longitudinal rehabilitation panel (2500 rows),
                     OMOP CDM v5.4 export (6 tables, sample patients only)

File format:         Apache Parquet (Snappy compression). Readable with pandas, polars,
                     pyarrow, R arrow, DuckDB, Spark.

Purpose:             evaluation of structure and content before licensing the full dataset.
                     The subset is small; subgroup proportions carry sampling noise and must
                     not be used for statistical inference.

Synthetic data:      all records are fully synthetic. No real patient data were used.

Full dataset:        15,000 patients / 20,054 limbs / 20,054 prostheses / 75,000 panel rows,
                     plus OMOP CDM export. See DATASET/ in the full delivery.

Sentinel Data, 2026.
