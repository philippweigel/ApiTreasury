import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import os


class XmlHandler:
    def __init__(self) -> None:
        pass

    def create_sample_camt053_data(data_list, file_io_api_key):
        # Root element
        root = ET.Element(
            "Document", xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"
        )

        # Loop over the data_list
        for data in data_list:
            b2c_statement = ET.SubElement(root, "BkToCstmrStmt")
            statement = ET.SubElement(b2c_statement, "Stmt")

            # Adding ID and Creation Date Time
            ET.SubElement(statement, "Id").text = data["statement_id"]
            ET.SubElement(statement, "CreDtTm").text = data["creation_date_time"]

            # Adding Opening Balance
            opening_balance = ET.SubElement(statement, "Bal")
            opening_balance_type = ET.SubElement(opening_balance, "Tp")
            ET.SubElement(opening_balance_type, "CdOrPrtry").text = data[
                "opening_balance_type"
            ]
            ET.SubElement(opening_balance, "Amt", Ccy=data["currency"]).text = str(
                data["opening_balance"]
            )

            # Adding transaction details
            entry = ET.SubElement(statement, "Ntry")
            ET.SubElement(entry, "Amt", Ccy=data["currency"]).text = str(
                data["entry_amount"]
            )
            ET.SubElement(entry, "CdtDbtInd").text = data["credit_debit_indicator"]
            transaction_details = ET.SubElement(entry, "NtryDtls")

            transaction = ET.SubElement(transaction_details, "TxDtls")
            ET.SubElement(transaction, "Refs", AcctSvcrRef=data["account_service_ref"])

            # Adding Closing Balance
            closing_balance = ET.SubElement(statement, "Bal")
            closing_balance_type = ET.SubElement(closing_balance, "Tp")
            ET.SubElement(closing_balance_type, "CdOrPrtry").text = data[
                "closing_balance_type"
            ]
            ET.SubElement(closing_balance, "Amt", Ccy=data["currency"]).text = str(
                data["closing_balance"]
            )

        # Creating XML file
        tree = ET.ElementTree(root)
        # Getting the current time and formatting it into a string
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Creating the file name with the timestamp
        file_name = f"data/camt053_{timestamp}.xml"

        # Save XML data to a file
        tree = ET.ElementTree(root)

        # Upload the file to file.io
        with open(file_name, "rb") as file:
            headers = {"Authorization": f"Bearer {file_io_api_key}"}
            response = requests.post(
                "https://file.io", files={"file": file}, headers=headers
            )
            if response.status_code == 200:
                download_link = response.json()["link"]
                print(f"File uploaded successfully. Download link: {download_link}")
                return download_link
            else:
                print("Failed to upload the file.")
                return None
