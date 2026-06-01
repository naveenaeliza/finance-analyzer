import pdfplumber
import pandas as pd
import re


def extract_text(pdf_path):

    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

    return full_text


def detect_bank(text):

    text = text.upper()

    if "SOUTHI NDIANBANK" in text.replace(" ", ""):
        return "SIB"

    if "STATE BANK OF INDIA" in text:
        return "SBI"

    if "HDFC BANK" in text:
        return "HDFC"

    return "UNKNOWN"


def parse_sib(text):

    lines = text.split("\n")

    transactions = []

    current_txn = None

    date_pattern = r"^\d{2}-\d{2}-\d{2}"

    amount_pattern = r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))"

    skip_words = [
        "STATEMENT OF ACCOUNT",
        "PAGE",
        "DATE PARTICULARS",
        "TYPE :",
        "CUSTOMER ID",
        "A/C NO",
        "IFSC",
        "MODE OF OPR",
        "CURRENCY CODE",
        "PAGE TOTAL",
        "GRAND TOTAL",
        "Visit us at"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if any(word in line for word in skip_words):
            continue

        if re.match(date_pattern, line):

            if current_txn:
                transactions.append(current_txn)

            current_txn = {
                "Date": "",
                "Description": "",
                "Amount": 0.0,
                "Type": "Debit"
            }

            parts = line.split()

            current_txn["Date"] = parts[0]

            amounts = re.findall(amount_pattern, line)

            if amounts:

                try:

                    amount = float(
                        amounts[-2].replace(",", "")
                    )

                    current_txn["Amount"] = amount

                except:
                    pass

            description = line.replace(parts[0], "")

            current_txn["Description"] = description.strip()

        else:

            if current_txn:

                current_txn["Description"] += " " + line

    if current_txn:
        transactions.append(current_txn)

    df = pd.DataFrame(transactions)

    return df


def clean_transactions(df):

    if df.empty:
        return df

    df["Description"] = (
        df["Description"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return df


def main():

    pdf_path = input(
        "Enter PDF path: "
    )

    text = extract_text(pdf_path)

    bank = detect_bank(text)

    print("\nDetected Bank:", bank)

    if bank == "SIB":

        df = parse_sib(text)

        df = clean_transactions(df)

        print("\nTransactions Found:")
        print(df.head(20))

        output_file = "transactions.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"\nSaved to {output_file}"
        )

    else:

        print(
            "\nUnknown bank format."
        )

        print(
            "Later we will use Gemini fallback."
        )


if __name__ == "__main__":
    main()