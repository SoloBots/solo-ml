import pyarrow.flight as flight

# Connect to the Flight Server
client = flight.FlightClient("grpc://localhost:8815")

# Request specific columns and time ranges via SQL
query = """
    SELECT 
    frame_number,
    FROM 'game.parquet'
    WHERE BallModel.valid IS true;
"""

ticket = flight.Ticket(query.encode('utf-8'))

# Stream the dataset directly into client memory
reader = client.do_get(ticket)
table = reader.read_all()

# Convert instantly to Pandas or Polars with zero serialization overhead
df = table.to_pandas()
print(df)