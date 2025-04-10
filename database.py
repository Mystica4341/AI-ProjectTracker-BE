from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database connection details
DATABASE_URL = "mssql+pyodbc://sa:12345@localhost/TrackingWebsite?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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