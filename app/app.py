from flask import Flask, jsonify, request, current_app
from bank_database import BankDatabase
import os
from dotenv import load_dotenv
from xml_handler import XmlHandler
import requests


def load_configurations(app):
    load_dotenv()
    app.config["DATABASE_NAME"] = os.getenv("DATABASE_NAME")
    app.config["DATABASE_USER"] = os.getenv("DATABASE_USER")
    app.config["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD")
    app.config["DATABASE_HOST"] = os.getenv("DATABASE_HOST")
    app.config["DATABASE_PORT"] = int(os.getenv("DATABASE_PORT"))
    app.config["FILE_IO_API_KEY"] = os.getenv("FILE_IO_API_KEY")


app = Flask(__name__)
load_configurations(app)

# Initialize the database
with app.app_context():
    db = BankDatabase()
    db.initialize()


# Transactions related routes and functions
@app.route("/transactions-api")
def get_transactions_api():
    transactions = db.execute_query("SELECT * FROM transactions_api")
    return jsonify({"transactions": transactions})


# Transactions related routes and functions
@app.route("/transactions-xml")
def get_transactions_xml():
    transactions = db.execute_query("SELECT * FROM transactions_xml")
    return jsonify({"transactions": transactions})


# data_raw related routes and functions
@app.route("/data-raw")
def get_data_raw():
    data_raw = db.execute_query("SELECT * FROM data_Raw")
    return jsonify({"data_raw": data_raw})


@app.route("/data-raw", methods=["POST"])
def add_data_raw():
    data = request.json
    statement_id = (
        data["statement_id"].strip()
        if isinstance(data["statement_id"], str)
        else data["statement_id"]
    )
    creation_date_time = data["creation_date_time"]
    opening_balance_type = (
        data["opening_balance_type"].strip()
        if isinstance(data["opening_balance_type"], str)
        else data["opening_balance_type"]
    )
    opening_balance = data["opening_balance"]
    entry_amount = data["entry_amount"]
    credit_debit_indicator = (
        data["credit_debit_indicator"].strip()
        if isinstance(data["credit_debit_indicator"], str)
        else data["credit_debit_indicator"]
    )
    account_service_ref = (
        data["account_service_ref"].strip()
        if isinstance(data["account_service_ref"], str)
        else data["account_service_ref"]
    )
    closing_balance_type = (
        data["closing_balance_type"].strip()
        if isinstance(data["closing_balance_type"], str)
        else data["closing_balance_type"]
    )
    closing_balance = data["closing_balance"]
    currency = (
        data["currency"].strip()
        if isinstance(data["currency"], str)
        else data["currency"]
    )

    try:
        db.execute_query(
            """
            INSERT INTO data_raw (statement_id, creation_date_time, opening_balance_type, opening_balance, entry_amount,
                      credit_debit_indicator, account_service_ref, closing_balance_type, closing_balance, currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                statement_id,
                creation_date_time,
                opening_balance_type,
                opening_balance,
                entry_amount,
                credit_debit_indicator,
                account_service_ref,
                closing_balance_type,
                closing_balance,
                currency,
            ),
            commit=True,
        )
        return jsonify({"message": "Data inserted successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/import-data-api")
def import_data_api():
    data = db.get_data_raw()
    return import_data_from_api_to_db(data, "transactions_api")


@app.route("/import-data-xml")
def import_data_xml():
    return db.import_transactions_from_camt053()


@app.route("/export-camt", methods=["POST"])
def export_camt():
    data = db.get_data_raw()
    file_io_api_key = current_app.config["FILE_IO_API_KEY"]
    return XmlHandler.create_sample_camt053_data(data["data_raw"], file_io_api_key)
    # return jsonify({"message": "Camt data created successfully!"}), 200


def import_data_from_api_to_db(data, table_name):
    try:
        # Check if data is a dictionary, if not raise an error
        if not isinstance(data, dict):
            raise ValueError("Expected data to be a dictionary")

        # Extract the "data_raw" key from the dictionary
        data = data["data_raw"]

        # Check if data is a list, if not convert it to list
        if not isinstance(data, list):
            data = [data]

        # Prepare the column names for the SQL query
        columns = "statement_id, creation_date_time, entry_amount, credit_debit_indicator, account_service_ref, currency"

        # Count the number of columns in the table
        num_columns = len(columns.split(", "))

        # Iterate over each record in the data
        for record in data:
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


if __name__ == "__main__":
    # with app.app_context():
    #     db = BankDatabase()
    #     db.initialize()

    app.run(debug=False)
