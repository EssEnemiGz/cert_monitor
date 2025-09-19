import psycopg2
import logging
import sys
import os

class DatabaseAdmin:
    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT")
            )
            self.cursor = self.conn.cursor()
            logging.info("Connected to the database")
        except psycopg2.OperationalError as e:
            logging.critical(f"Cannot connect to the database: {e}")
            sys.exit(1)

    def commit(self):
        if self.conn != None:
            self.conn.commit()
        else:
            logging.error("Cursor is None, cannot commit changes.")
            sys.exit(1)

    def save_domain(self, domain):
        if self.cursor == None:
            logging.error("Cursor is None, try to connect to the database first.")
            sys.exit(1)

        if domain.startswith('*.'):
            domain = domain[2:]

        try:
            self.cursor.execute(
                "INSERT INTO domains (domain) VALUES (%s) ON CONFLICT (domain) DO NOTHING;",
                (domain,)
            )
        except psycopg2.Error as e:
            logging.error(f"Error saving the domain '{domain}': {e}")
