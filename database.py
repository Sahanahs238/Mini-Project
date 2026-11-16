import pyodbc

def connect_db():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-HQJV6BL6\\SQLEXPRESS;"
        "DATABASE=Gym_Diet_DB;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return conn