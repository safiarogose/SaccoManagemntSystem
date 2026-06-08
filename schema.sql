CREATE TABLE branch (
    branch_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_code VARCHAR(30) NOT NULL UNIQUE,
    branch_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(30),
    email VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL
);

CREATE TABLE role (
    role_id INT IDENTITY(1,1) PRIMARY KEY,
    role_name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE staff (
    staff_id INT IDENTITY(1,1) PRIMARY KEY,
    staff_no VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    gender CHAR(1),
    phone VARCHAR(30),
    email VARCHAR(100),
    role_id INT NOT NULL,
    branch_id INT NOT NULL,
    date_hired DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,
    CONSTRAINT fk_staff_role FOREIGN KEY (role_id) REFERENCES role(role_id),
    CONSTRAINT fk_staff_branch FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE member (
    member_id INT IDENTITY(1,1) PRIMARY KEY,
    member_no VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    middle_name VARCHAR(80),
    last_name VARCHAR(80) NOT NULL,
    gender CHAR(1),
    date_of_birth DATE,
    id_no VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(30),
    email VARCHAR(100),
    address VARCHAR(255),
    date_joined DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    branch_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,
    CONSTRAINT fk_member_branch FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);

CREATE TABLE account_type (
    account_type_id INT IDENTITY(1,1) PRIMARY KEY,
    type_name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE product (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    product_category VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
);

CREATE TABLE account (
    account_id INT IDENTITY(1,1) PRIMARY KEY,
    account_no VARCHAR(40) NOT NULL UNIQUE,
    account_type_id INT NOT NULL,
    member_id INT NOT NULL,
    product_id INT NOT NULL,
    opening_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    current_balance DECIMAL(18,2) NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,
    CONSTRAINT fk_account_type FOREIGN KEY (account_type_id) REFERENCES account_type(account_type_id),
    CONSTRAINT fk_account_member FOREIGN KEY (member_id) REFERENCES member(member_id),
    CONSTRAINT fk_account_product FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT ck_account_balance CHECK (current_balance >= 0)
);

CREATE TABLE transaction_type (
    transaction_type_id INT IDENTITY(1,1) PRIMARY KEY,
    type_name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE payment_method (
    payment_method_id INT IDENTITY(1,1) PRIMARY KEY,
    method_name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
);

CREATE TABLE account_transaction (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    account_id INT NOT NULL,
    transaction_date DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    transaction_type_id INT NOT NULL,
    payment_method_id INT NULL,
    amount DECIMAL(18,2) NOT NULL,
    balance_after DECIMAL(18,2) NOT NULL,
    narration VARCHAR(255),
    created_by INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_transaction_account FOREIGN KEY (account_id) REFERENCES account(account_id),
    CONSTRAINT fk_transaction_type FOREIGN KEY (transaction_type_id) REFERENCES transaction_type(transaction_type_id),
    CONSTRAINT fk_transaction_payment_method FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id),
    CONSTRAINT fk_transaction_staff FOREIGN KEY (created_by) REFERENCES staff(staff_id),
    CONSTRAINT ck_transaction_amount CHECK (amount > 0)
);

CREATE TABLE loan_type (
    loan_type_id INT IDENTITY(1,1) PRIMARY KEY,
    type_name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE loan (
    loan_id INT IDENTITY(1,1) PRIMARY KEY,
    loan_no VARCHAR(40) NOT NULL UNIQUE,
    member_id INT NOT NULL,
    product_id INT NOT NULL,
    loan_type_id INT NOT NULL,
    application_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    approval_date DATE NULL,
    loan_amount DECIMAL(18,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    repayment_period INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Applied',
    disbursement_date DATE NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,
    CONSTRAINT fk_loan_member FOREIGN KEY (member_id) REFERENCES member(member_id),
    CONSTRAINT fk_loan_product FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT fk_loan_type FOREIGN KEY (loan_type_id) REFERENCES loan_type(loan_type_id),
    CONSTRAINT ck_loan_amount CHECK (loan_amount > 0),
    CONSTRAINT ck_loan_interest CHECK (interest_rate >= 0),
    CONSTRAINT ck_loan_period CHECK (repayment_period > 0)
);

CREATE TABLE guarantor (
    guarantor_id INT IDENTITY(1,1) PRIMARY KEY,
    member_id INT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    id_no VARCHAR(50),
    phone VARCHAR(30),
    email VARCHAR(100),
    address VARCHAR(255),
    CONSTRAINT fk_guarantor_member FOREIGN KEY (member_id) REFERENCES member(member_id)
);

CREATE TABLE loan_guarantor (
    loan_id INT NOT NULL,
    guarantor_id INT NOT NULL,
    guaranteed_amount DECIMAL(18,2) NULL,
    PRIMARY KEY (loan_id, guarantor_id),
    CONSTRAINT fk_loan_guarantor_loan FOREIGN KEY (loan_id) REFERENCES loan(loan_id),
    CONSTRAINT fk_loan_guarantor_guarantor FOREIGN KEY (guarantor_id) REFERENCES guarantor(guarantor_id)
);

CREATE TABLE loan_repayment (
    repayment_id INT IDENTITY(1,1) PRIMARY KEY,
    loan_id INT NOT NULL,
    repayment_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    installment_no INT NOT NULL,
    amount_paid DECIMAL(18,2) NOT NULL,
    principal DECIMAL(18,2) NOT NULL DEFAULT 0,
    interest DECIMAL(18,2) NOT NULL DEFAULT 0,
    balance_outstanding DECIMAL(18,2) NOT NULL,
    payment_method_id INT NOT NULL,
    received_by INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_repayment_loan FOREIGN KEY (loan_id) REFERENCES loan(loan_id),
    CONSTRAINT fk_repayment_payment_method FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id),
    CONSTRAINT fk_repayment_staff FOREIGN KEY (received_by) REFERENCES staff(staff_id),
    CONSTRAINT ck_repayment_amount CHECK (amount_paid > 0),
    CONSTRAINT ck_repayment_principal CHECK (principal >= 0),
    CONSTRAINT ck_repayment_interest CHECK (interest >= 0),
    CONSTRAINT ck_repayment_balance CHECK (balance_outstanding >= 0)
);

CREATE INDEX ix_member_branch ON member(branch_id);
CREATE INDEX ix_account_member ON account(member_id);
CREATE INDEX ix_account_product ON account(product_id);
CREATE INDEX ix_transaction_account_date ON account_transaction(account_id, transaction_date);
CREATE INDEX ix_loan_member ON loan(member_id);
CREATE INDEX ix_loan_status ON loan(status);
CREATE INDEX ix_repayment_loan_date ON loan_repayment(loan_id, repayment_date);

INSERT INTO role (role_name, description) VALUES
('Administrator', 'Manages users, roles, branches, and system settings'),
('Manager', 'Approves loans and supervises SACCO operations'),
('Loans Officer', 'Processes loan applications and guarantors'),
('Teller', 'Posts deposits, withdrawals, and repayments'),
('Accountant', 'Reviews financial records and reports'),
('Auditor', 'Reviews audit and compliance records');

INSERT INTO account_type (type_name, description) VALUES
('Savings', 'Member savings account'),
('Welfare', 'Member welfare contribution account'),
('Share Capital', 'Member share capital account'),
('Loan', 'Loan control account');

INSERT INTO transaction_type (type_name, description) VALUES
('Deposit', 'Money paid into an account'),
('Withdrawal', 'Money paid out of an account'),
('Loan Disbursement', 'Approved loan paid to member'),
('Loan Repayment', 'Loan repayment received'),
('Charge', 'Account or loan charge'),
('Adjustment', 'Approved correction entry'),
('Interest Posting', 'Interest credited or charged');

INSERT INTO payment_method (method_name, description, status) VALUES
('Cash', 'Cash payment', 'Active'),
('Bank Transfer', 'Bank transfer payment', 'Active'),
('Mobile Money', 'Mobile money payment', 'Active'),
('Payroll Deduction', 'Deduction from salary or payroll', 'Active');

INSERT INTO loan_type (type_name, description) VALUES
('Normal Loan', 'Standard member loan'),
('Emergency Loan', 'Short-term emergency loan'),
('School Fees Loan', 'Education support loan'),
('Asset Loan', 'Asset acquisition loan'),
('Welfare Loan', 'Welfare support loan');

INSERT INTO product (product_name, description, product_category, status) VALUES
('Ordinary Savings', 'Regular member savings product', 'Savings', 'Active'),
('Welfare Fund', 'Member welfare contribution product', 'Savings', 'Active'),
('Share Capital', 'Member share capital product', 'Savings', 'Active'),
('Normal Loan Product', 'Standard SACCO loan product', 'Loan', 'Active'),
('Emergency Loan Product', 'Emergency SACCO loan product', 'Loan', 'Active');
