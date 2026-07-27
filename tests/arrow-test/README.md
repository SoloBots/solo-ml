# Apache Arrow Test
Currently we store our log data in a row like format meaning first all data from the first timestamp and then all data from the second timestamp and so on. For later analysis this is not convenient. To analyze IMU data we need to parse the whole binary log.
We can improve performance slightly by first creating an index of all the data and use this to access the data. 

A better way is to first convert a log file to a columnar storage format like a parquet file and then query this file with Apache Arrow.

## Run test
download game.log from https://logs.berlin-united.com/2026-06-30-RC26/2026-07-05_12-00_Berlin%20United_vs_KHUBER_half2/3_33_Nao0022_260705-0325/

```bash
uv sync
uv run parquet_converter.py
```

run flight-server.py in one terminal and client.py in another