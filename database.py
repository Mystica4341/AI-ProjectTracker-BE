from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

#read .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
qdrant_client = QdrantClient(
    host = QDRANT_HOST,
    api_key= QDRANT_API_KEY,
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