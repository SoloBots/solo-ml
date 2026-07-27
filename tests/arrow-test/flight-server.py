import pyarrow.flight as flight
import duckdb

class RobotLogFlightServer(flight.FlightServerBase):
    def do_get(self, context, ticket):
        # Decode the query sent by the client
        query = ticket.ticket.decode('utf-8')
        
        # Run the query directly on Parquet logs via DuckDB
        # DuckDB returns an Arrow Table reader
        arrow_table = duckdb.query(query).arrow()
        
        # Stream the Arrow record batches directly to the client
        return flight.RecordBatchStream(arrow_table)

if __name__ == '__main__':
    server = RobotLogFlightServer("grpc://0.0.0.0:8815")
    print("Arrow Flight Server running on port 8815...")
    server.serve()