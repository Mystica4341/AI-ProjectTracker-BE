from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient

# Replace with your actual database connection details
DATABASE_URL = "mssql+pyodbc://sa:12345@localhost/TrackingWebsite?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
qdrant_client = QdrantClient(
    host = '49e3e764-01cb-441e-8910-b4bcc220aa17.us-east-1-0.aws.cloud.qdrant.io',
    api_key= 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.CN3ZUe9y5skPuYA_wc5b_j1-5yfv4BPEnsw62UmeI-k',
    port= 6333
)
# Test the connection
# try:
#     with engine.connect() as connection:
#         print("Connection successful!")
#         # Example: Execute a query
#         result = connection.execute("SELECT TOP 10 * FROM your_table_name")  # Replace with your table name
#         for row in result:
#             print(row)
# except Exception as e:
#     print("Error:", e)