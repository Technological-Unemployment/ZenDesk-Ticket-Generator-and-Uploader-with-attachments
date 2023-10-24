import psycopg2 as pg
import pandas as pd

DB_CONFIG = {
    "dbname": "your_dbname",
    "host": "your_host",
    "port": "5439",
    "user": "username",
    "password": "password",
}

def create_connection():
    return pg.connect(**DB_CONFIG)

def execute_query(query):
    try:
        connection = create_connection()
        df = pd.read_sql_query(query, con=connection)
        connection.close()
        return df
    except (Exception, pg.DatabaseError) as error:
        print("Error while connecting to PostgreSQL database: ", error)
        return None

def QsearchT(name):
    query = f"""Add your SQL Query to generate trend charts by name;
                WHERE name = '{name}'"""
    return execute_query(query)

def QsearchD(name):
    query = f"""Add your SQL Query to generate density charts by name;
                WHERE name = '{name}'"""
    return execute_query(query)
