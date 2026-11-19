Working with Apache Parquet
===========================

Python:
  import pandas as pd
  df = pd.read_parquet('patients_observed.parquet')

The profile table is large. Read it in pieces:
  import pyarrow.parquet as pq
  pf = pq.ParquetFile('pk_profiles.parquet')
  for batch in pf.iter_batches(batch_size=1_000_000):
      chunk = batch.to_pandas()

Or filter by patient with DuckDB:
  import duckdb
  duckdb.sql("select * from 'pk_profiles.parquet' where patient_id = 1 and regimen = 'A'").df()

R: arrow::read_parquet('patients_observed.parquet')

Join key across all patient tables: patient_id. Regimen tables also carry regimen (A to E).
List columns (seg_start_h, seg_dur_h, seg_rate_mg_h) arrive as arrays in pandas.

This archive holds 400 patients: 200 on meropenem and 200 on piperacillin, all five regimens each, drawn at random from the full release with a fixed seed.
