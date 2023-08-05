from flask import Flask, jsonify, request
from bank_database import BankDatabase
import os
from dotenv import load_dotenv
from xml_handler import XmlHandler


def load_configurations(app):
    load_dotenv()
    app.config["DATABASE_NAME"] = os.getenv("DATABASE_NAME")
    app.config["DATABASE_USER"] = os.getenv("DATABASE_USER")
    app.config["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD")
    app.config["DATABASE_HOST"] = os.getenv("DATABASE_HOST")
    app.config["DATABASE_PORT"] = int(os.getenv("DATABASE_PORT"))


app = Flask(__name__)
load_configurations(app)
db = BankDatabase()
db.initialize()


# Statements related routes and functions
@app.route("/statements")
def get_statements():
    statements = db.execute_query("SELECT * FROM statements")
    return jsonify({"statements": statements})


@app.route("/statements/<int:id>")
def get_statements_by_id(id):
    query = "SELECT * FROM statements WHERE id = %s"  # Use %s as a placeholder for the parameter
    statement = db.execute_query(query, (id,), fetchone=True)

    if statement:
        return jsonify({"statement": statement})
    else:
        return jsonify({"message": "Statement not found"}), 404


# Transactions related routes and functions
@app.route("/transactions")
def get_transactions():
    transactions = db.execute_query("SELECT * FROM transactions")
    return jsonify({"transactions": transactions})


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
    return db.import_data_from_api_to_db(
        "http://localhost:5000/data-raw", "transactions_api"
    )


@app.route("/import-data-xml")
def import_data_xml():
    data = db.get_data_raw()
    XmlHandler.create_sample_camt053_data(data)
    return db.import_transactions_from_camt053()


if __name__ == "__main__":
    with app.app_context():
        db = BankDatabase()
        db.initialize()

    app.run(debug=False)
