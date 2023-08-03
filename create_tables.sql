-- SQL statement to create the bank_accounts table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id SERIAL PRIMARY KEY,
    account_number TEXT NOT NULL,
    account_holder_name TEXT NOT NULL,
    balance NUMERIC NOT NULL
);

-- SQL statement to create the payments table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    sender_account_id INTEGER NOT NULL,
    receiver_account_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (sender_account_id) REFERENCES bank_accounts(id),
    FOREIGN KEY (receiver_account_id) REFERENCES bank_accounts(id)
);
