# Parliamentary Police Saving Welfare SACCO System

This project contains a starter system design for a SACCO serving Parliamentary Police members. It is based on the supplied ERD and covers member registration, accounts, savings products, loans, guarantors, repayments, transactions, staff, roles, and branches.

## Core Modules

1. Member management
   - Register members with member number, names, gender, date of birth, ID number, phone, email, address, branch, joining date, and status.
   - Track active, inactive, suspended, retired, or exited members.

2. Branch and staff management
   - Maintain SACCO branches or offices.
   - Register staff, assign roles, and link staff to branches.
   - Use roles such as Administrator, Manager, Loans Officer, Teller, Accountant, and Auditor.

3. Products and account management
   - Configure savings, welfare, share capital, emergency fund, and loan products.
   - Open member accounts by product and account type.
   - Maintain current account balances.

4. Transaction management
   - Record deposits, withdrawals, charges, transfers, adjustments, and interest postings.
   - Keep transaction date, transaction type, amount, balance after transaction, narration, and staff creator.

5. Loan management
   - Receive loan applications.
   - Track approval date, approved amount, interest rate, repayment period, status, and disbursement date.
   - Support loan types such as normal loan, emergency loan, school fees loan, asset loan, and welfare loan.

6. Guarantor management
   - Register guarantors.
   - Link one or more guarantors to each loan.
   - Support guarantors who are SACCO members.

7. Loan repayment management
   - Record repayments by installment number.
   - Split repayment into principal and interest.
   - Track outstanding balance, payment method, and receiving staff.

8. Reporting
   - Member register
   - Account balances
   - Savings statement
   - Loan portfolio
   - Loan arrears
   - Repayment schedule
   - Cashier/teller collections
   - Branch performance
   - Audit trail

## Recommended User Roles

| Role | Main Permissions |
| --- | --- |
| Administrator | Manage system settings, roles, staff, branches, products |
| Manager | Approve loans, view reports, supervise branch activity |
| Loans Officer | Register applications, manage guarantors, monitor repayments |
| Teller | Post deposits, withdrawals, and repayments |
| Accountant | Review transactions, balances, and financial reports |
| Auditor | View reports and audit transaction history |

## Main Workflows

### Member Registration

1. Staff captures member details.
2. System validates unique member number and ID number.
3. Member is assigned to a branch.
4. Default accounts can be opened for savings, welfare, or share capital.
5. Member status is set to active.

### Savings Deposit

1. Teller selects member account.
2. Teller enters amount, payment method, and narration.
3. System records the transaction.
4. System updates account current balance.
5. Receipt or statement line is generated.

### Loan Application

1. Loans officer selects member and product.
2. Officer enters loan amount, loan type, interest rate, and repayment period.
3. Guarantors are attached.
4. Manager reviews and approves or rejects.
5. Approved loan is disbursed and repayment schedule begins.

### Loan Repayment

1. Teller selects loan.
2. Teller enters repayment amount and payment method.
3. System splits amount into principal and interest according to SACCO rules.
4. Outstanding loan balance is updated.
5. Repayment record and transaction entry are saved.

## Suggested Status Values

| Entity | Status Values |
| --- | --- |
| Member | Active, Inactive, Suspended, Exited, Retired |
| Staff | Active, Suspended, Left |
| Product | Active, Inactive |
| Account | Active, Dormant, Closed |
| Loan | Applied, Approved, Rejected, Disbursed, Running, Cleared, Defaulted, WrittenOff |
| Payment Method | Active, Inactive |

## Non-Functional Requirements

- Every monetary operation must be auditable.
- Account balances should be updated inside database transactions.
- Member number, staff number, account number, loan number, and ID number should be unique.
- Users should only access actions allowed by their role.
- Reports should support filtering by date range, branch, product, member, and status.
- The system should keep timestamps for creation and updates.
- Sensitive data should be protected through secure login, strong passwords, and proper access control.

## Files

- `index.html` opens a clickable SACCO prototype in the browser.
- `styles.css` contains the prototype layout and visual design.
- `app.js` contains sample data and simple screen navigation.
- `manage.py` runs the Django development server.
- `sacco_system/` contains Django project settings and URL configuration.
- `core/` contains the Django app that serves the prototype.
- `schema.sql` contains a relational database schema based on the ERD.
- `procedures.sql` contains starter SQL Server procedures for posting account transactions, approving loans, and recording repayments.
- `SYSTEM_DESIGN.md` contains the functional design, screen design, permissions, business rules, and recommended technology stack.
- `REPORTS.md` contains report definitions, columns, and filters.

## Run The Django System

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_demo
py manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

Demo login:

```text
Username: admin
Password: admin123
```

## Deployment Check

```powershell
py manage.py collectstatic --noinput
$env:DJANGO_DEBUG="False"
$env:DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
$env:DJANGO_ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
$env:DJANGO_CSRF_TRUSTED_ORIGINS="https://your-domain.com,https://www.your-domain.com"
py manage.py check --deploy
```

See `DEPLOYMENT.md` for production environment settings.
