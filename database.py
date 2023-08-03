import psycopg2
from flask import current_app


class BankDatabase:
    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        return psycopg2.connect(
            dbname=current_app.config["DATABASE_NAME"],
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            host=current_app.config["DATABASE_HOST"],
            port=current_app.config["DATABASE_PORT"],
        )

    def read_sql_from_file(self, file_path):
        with open(file_path, "r") as file:
            return file.read()

    def create_tables(self):
        # Read SQL statements from the file
        sql_statements = self.read_sql_from_file("create_tables.sql")

        # Execute the SQL statements
        with self.connection:
            self.connection.cursor().execute(sql_statements)

    def close(self):
        self.connection.close()

    def execute_query(self, query, params=None, fetchone=False):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone() if fetchone else cursor.fetchall()

    def initialize(self):
        self.create_tables()

        # Check if there are existing records in the bank_accounts table
        if not self.execute_query("SELECT 1 FROM bank_accounts LIMIT 1"):
            self.insert_bank_accounts()

        # Check if there are existing records in the payments table
        if not self.execute_query("SELECT 1 FROM payments LIMIT 1"):
            self.insert_payments()

    def insert_bank_accounts(self):
        bank_accounts_data = [
            ("123456789", "John Doe", 1000.50),
            ("987654321", "Jane Smith", 500.25),
            ("456789123", "Bob Johnson", 750.80),
        ]
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO bank_accounts (account_number, account_holder_name, balance) VALUES (%s, %s, %s)",
                    bank_accounts_data,
                )

    def insert_payments(self):
        payments_data = [
            (1, 2, 200.75, "2023-07-31 12:34:56"),
            (3, 1, 100.0, "2023-07-31 14:23:45"),
            (2, 3, 50.50, "2023-07-31 16:01:02"),
        ]
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO payments (sender_account_id, receiver_account_id, amount, timestamp) VALUES (%s, %s, %s, %s)",
                    payments_data,
                )

    def select_data(self):
        bank_accounts_data = self.execute_query("SELECT * FROM bank_accounts")
        payments_data = self.execute_query("SELECT * FROM payments")
        return bank_accounts_data, payments_data
