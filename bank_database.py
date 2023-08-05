import psycopg2
from flask import current_app, jsonify
import os
from xml_handler import XmlHandler
import xml.etree.ElementTree as ET
import shutil
import requests


class BankDatabase:
    def __init__(self):
        self.connection = self.create_connection()
        self.xml_handler = XmlHandler()

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

    def execute_query(self, query, params=None, fetchone=False, commit=False):
        if self.connection.closed:
            self.connection = self.create_connection()
        # else:
        #     self.connection.rollback()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if commit:
                    self.connection.commit()
                    return {"message": "Operation executed successfully!"}

                col_names = [desc[0] for desc in cursor.description]

                def build_row(row):
                    return {col_name: value for col_name, value in zip(col_names, row)}

                data = cursor.fetchone() if fetchone else cursor.fetchall()
                return build_row(data) if fetchone else [build_row(row) for row in data]
        except Exception as e:
            print(f"Failed to execute query: {e}")
            self.connection.rollback()
            return None

    def initialize(self):
        self.create_tables()

    def get_data_raw(self):
        data_raw = self.execute_query(
            """
        SELECT statement_id, creation_date_time, opening_balance_type, opening_balance, entry_amount,
                      credit_debit_indicator, account_service_ref, closing_balance_type, closing_balance, currency
        FROM data_raw
        """
        )
        for item in data_raw:
            item["creation_date_time"] = item["creation_date_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            item["opening_balance"] = str(item["opening_balance"])
            item["entry_amount"] = str(item["entry_amount"])
            item["closing_balance"] = str(item["closing_balance"])

        return data_raw

    def import_transactions_from_camt053(self):
        processed_dir = "data/processed/"

        # Create processed directory if it does not exist
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)

        # Iterating through every file in the directory
        for filename in os.listdir("data/"):
            if not filename.endswith(".xml"):  # Skip non-XML files
                continue

            filepath = os.path.join("data/", filename)  # Create full file path

            # Open the CAMT053 XML file
            tree = ET.parse(filepath)
            root = tree.getroot()

            ns = {"ns": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"}

            # Iterate through the statements in the XML file
            for stmt in root.findall(".//ns:Stmt", ns):
                statement_id = stmt.find(".//ns:Id", ns).text
                creation_date_time = stmt.find(".//ns:CreDtTm", ns).text

                # Iterate through the transactions for this statement
                for ntry in stmt.findall(".//ns:Ntry", ns):
                    entry_amount = ntry.find("ns:Amt", ns).text
                    currency = ntry.find("ns:Amt", ns).attrib["Ccy"]
                    credit_debit_indicator = ntry.find("ns:CdtDbtInd", ns).text
                    account_service_ref = ntry.find(".//ns:Refs", ns).attrib[
                        "AcctSvcrRef"
                    ]

                    # Insert the transaction into the database
                    with self.connection:
                        with self.connection.cursor() as cursor:
                            cursor.execute(
                                """
                                INSERT INTO transactions_xml (statement_id, creation_date_time, entry_amount, credit_debit_indicator, account_service_ref, currency)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    statement_id,
                                    creation_date_time,
                                    entry_amount,
                                    credit_debit_indicator,
                                    account_service_ref,
                                    currency,
                                ),
                            )
                            self.connection.commit()

            # Move the processed XML file to the processed directory
            shutil.move(filepath, os.path.join(processed_dir, filename))

        return jsonify({"message": "Data imported successfully!"}), 200

    def import_data_from_api_to_db(api_url, table_name):
        try:
            # Fetch data from the API
            response = requests.get(api_url)
            response.raise_for_status()

            # Parse the JSON data
            data = response.json()

            # Check if data is a list, if not convert it to list
            if not isinstance(data["data_raw"], list):
                data["data_raw"] = [data["data_raw"]]

            # Prepare the column names for the SQL query
            columns = "statement_id, creation_date_time, entry_amount, credit_debit_indicator, account_service_ref, currency"

            # Count the number of columns in the table
            num_columns = len(columns.split(", "))

            # Iterate over each record in the data
            for record in data["data_raw"]:
                # Ensure record is dictionary
                if not isinstance(record, dict):
                    raise ValueError("Expected record to be a dictionary")

                # Prepare a SQL INSERT statement
                placeholders = ", ".join(["%s"] * num_columns)
                sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (
                    table_name,
                    columns,
                    placeholders,
                )

                # Create a tuple of values in the order they appear in the SQL query
                values = (
                    record.get("statement_id"),
                    record.get("creation_date_time"),
                    record.get("entry_amount"),
                    record.get("credit_debit_indicator"),
                    record.get("account_service_ref"),
                    record.get("currency"),
                )
                print(values)
                # Execute the SQL statement
                try:
                    db.execute_query(sql, values, commit=True)
                except Exception as e:
                    print(f"Failed to insert record {values}. Error: {e}")
                    continue

            return jsonify({"message": "Data imported successfully!"}), 200

        except requests.HTTPError as http_err:
            return jsonify({"error": f"HTTP error occurred: {http_err}"}), 400
        except Exception as err:
            return jsonify({"error": f"An error occurred: {err}"}), 400
