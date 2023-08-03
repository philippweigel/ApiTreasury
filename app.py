from flask import Flask, jsonify, current_app
import psycopg2
from database import BankDatabase
import os
from dotenv import load_dotenv


def load_configurations(app):
    load_dotenv()
    app.config["DATABASE_NAME"] = os.getenv("DATABASE_NAME")
    app.config["DATABASE_USER"] = os.getenv("DATABASE_USER")
    app.config["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD")
    app.config["DATABASE_HOST"] = os.getenv("DATABASE_HOST")
    app.config["DATABASE_PORT"] = int(os.getenv("DATABASE_PORT"))


app = Flask(__name__)
load_configurations(app)


# Bank Account related routes and functions
@app.route("/bank_accounts")
def get_bank_accounts():
    bank_accounts_data = db.execute_query("SELECT * FROM bank_accounts")
    return jsonify({"bank_accounts": bank_accounts_data})


@app.route("/bank_accounts/<int:account_id>")
def get_bank_account(account_id):
    query = "SELECT * FROM bank_accounts WHERE id = %s"  # Use %s as a placeholder for the parameter
    bank_account_data = db.execute_query(query, (account_id,), fetchone=True)

    if bank_account_data:
        return jsonify({"bank_account": bank_account_data})
    else:
        return jsonify({"message": "Bank account not found"}), 404


# Payment related routes and functions
@app.route("/payments")
def get_payments():
    payments_data = db.execute_query("SELECT * FROM payments")
    return jsonify({"payments": payments_data})


@app.route("/bank_accounts/<int:account_id>/payments")
def get_payment_history(account_id):
    query = "SELECT * FROM payments WHERE sender_account_id = %s OR receiver_account_id = %s"  # Use %s as placeholders for the parameters
    payment_history = db.execute_query(query, (account_id, account_id))

    if payment_history:
        return jsonify({"payment_history": payment_history})
    else:
        return jsonify({"message": "Payment history not found"}), 404


if __name__ == "__main__":
    with app.app_context():
        db = BankDatabase()
        db.initialize()

    app.run(debug=True)
