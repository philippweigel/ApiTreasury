-- CREATE TABLE IF NOT EXISTS statements (
--     id SERIAL PRIMARY KEY,
--     stmt_id VARCHAR(255),
--     created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     opening_balance DECIMAL(18, 2),
--     opening_balance_currency CHAR(3),
--     closing_balance DECIMAL(18, 2),
--     closing_balance_currency CHAR(3)
-- );

-- CREATE TABLE IF NOT EXISTS transactions (
--     id SERIAL PRIMARY KEY,
--     statement_id INT REFERENCES statements(id),
--     amount DECIMAL(18, 2),
--     currency CHAR(3),
--     credit_debit VARCHAR(5),
--     account_service_ref VARCHAR(255),
--     created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE IF NOT EXISTS data_raw (
    id SERIAL PRIMARY KEY,
    statement_id VARCHAR(255),
    creation_date_time TIMESTAMP,
    opening_balance_type CHAR(5),
    opening_balance DECIMAL(18,2),
    entry_amount DECIMAL(18,2),
    credit_debit_indicator CHAR(5),
    account_service_ref VARCHAR(255),
    closing_balance_type CHAR(5),
    closing_balance DECIMAL(18,2),
    currency CHAR(3),
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions_xml(
    id SERIAL PRIMARY KEY,
    statement_id VARCHAR(255),
    creation_date_time TIMESTAMP,
    entry_amount DECIMAL(18,2),
    credit_debit_indicator CHAR(5),
    account_service_ref VARCHAR(255),
    currency CHAR(3),
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions_api(
    id SERIAL PRIMARY KEY,
    statement_id VARCHAR(255),
    creation_date_time TIMESTAMP,
    entry_amount DECIMAL(18,2),
    credit_debit_indicator CHAR(5),
    account_service_ref VARCHAR(255),
    currency CHAR(3),
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
