CREATE OR ALTER PROCEDURE post_account_transaction
    @account_id INT,
    @transaction_type_id INT,
    @payment_method_id INT = NULL,
    @amount DECIMAL(18,2),
    @narration VARCHAR(255),
    @created_by INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @type_name VARCHAR(80);
    DECLARE @current_balance DECIMAL(18,2);
    DECLARE @new_balance DECIMAL(18,2);

    IF @amount <= 0
    BEGIN
        THROW 50001, 'Transaction amount must be greater than zero.', 1;
    END;

    BEGIN TRANSACTION;

    SELECT @type_name = type_name
    FROM transaction_type
    WHERE transaction_type_id = @transaction_type_id;

    SELECT @current_balance = current_balance
    FROM account WITH (UPDLOCK, ROWLOCK)
    WHERE account_id = @account_id
      AND status = 'Active';

    IF @current_balance IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50002, 'Active account was not found.', 1;
    END;

    SET @new_balance =
        CASE
            WHEN @type_name IN ('Withdrawal', 'Charge') THEN @current_balance - @amount
            ELSE @current_balance + @amount
        END;

    IF @new_balance < 0
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50003, 'Transaction would create a negative account balance.', 1;
    END;

    UPDATE account
    SET current_balance = @new_balance,
        updated_at = SYSUTCDATETIME()
    WHERE account_id = @account_id;

    INSERT INTO account_transaction (
        account_id,
        transaction_type_id,
        payment_method_id,
        amount,
        balance_after,
        narration,
        created_by
    )
    VALUES (
        @account_id,
        @transaction_type_id,
        @payment_method_id,
        @amount,
        @new_balance,
        @narration,
        @created_by
    );

    COMMIT TRANSACTION;
END;
GO

CREATE OR ALTER PROCEDURE approve_loan
    @loan_id INT,
    @approved_by INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (
        SELECT 1
        FROM loan_guarantor
        WHERE loan_id = @loan_id
    )
    BEGIN
        THROW 51001, 'Loan must have at least one guarantor before approval.', 1;
    END;

    UPDATE loan
    SET status = 'Approved',
        approval_date = CAST(GETDATE() AS DATE),
        updated_at = SYSUTCDATETIME()
    WHERE loan_id = @loan_id
      AND status = 'Applied';

    IF @@ROWCOUNT = 0
    BEGIN
        THROW 51002, 'Only applied loans can be approved.', 1;
    END;
END;
GO

CREATE OR ALTER PROCEDURE record_loan_repayment
    @loan_id INT,
    @installment_no INT,
    @amount_paid DECIMAL(18,2),
    @principal DECIMAL(18,2),
    @interest DECIMAL(18,2),
    @payment_method_id INT,
    @received_by INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @loan_amount DECIMAL(18,2);
    DECLARE @total_principal_paid DECIMAL(18,2);
    DECLARE @balance_outstanding DECIMAL(18,2);

    IF @amount_paid <= 0 OR @principal < 0 OR @interest < 0
    BEGIN
        THROW 52001, 'Invalid repayment amounts.', 1;
    END;

    IF @amount_paid <> @principal + @interest
    BEGIN
        THROW 52002, 'Amount paid must equal principal plus interest.', 1;
    END;

    BEGIN TRANSACTION;

    SELECT @loan_amount = loan_amount
    FROM loan WITH (UPDLOCK, ROWLOCK)
    WHERE loan_id = @loan_id
      AND status IN ('Disbursed', 'Running');

    IF @loan_amount IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 52003, 'Running or disbursed loan was not found.', 1;
    END;

    SELECT @total_principal_paid = COALESCE(SUM(principal), 0)
    FROM loan_repayment
    WHERE loan_id = @loan_id;

    SET @balance_outstanding = @loan_amount - @total_principal_paid - @principal;

    IF @balance_outstanding < 0
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 52004, 'Repayment principal exceeds outstanding loan balance.', 1;
    END;

    INSERT INTO loan_repayment (
        loan_id,
        installment_no,
        amount_paid,
        principal,
        interest,
        balance_outstanding,
        payment_method_id,
        received_by
    )
    VALUES (
        @loan_id,
        @installment_no,
        @amount_paid,
        @principal,
        @interest,
        @balance_outstanding,
        @payment_method_id,
        @received_by
    );

    UPDATE loan
    SET status = CASE WHEN @balance_outstanding = 0 THEN 'Cleared' ELSE 'Running' END,
        updated_at = SYSUTCDATETIME()
    WHERE loan_id = @loan_id;

    COMMIT TRANSACTION;
END;
GO
