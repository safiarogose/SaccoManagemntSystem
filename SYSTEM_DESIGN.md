# System Design

## System Name

Parliamentary Police Saving Welfare SACCO Management System

## Purpose

The system manages SACCO members, savings, welfare contributions, share capital, loans, guarantors, repayments, staff, branches, and reports for Parliamentary Police Saving Welfare SACCO.

## Main Users

| User | Responsibility |
| --- | --- |
| Administrator | Creates staff users, roles, branches, products, and system settings |
| SACCO Manager | Approves loans, supervises operations, reviews reports |
| Loans Officer | Registers loan applications, guarantors, and loan follow-up notes |
| Teller | Receives deposits, posts withdrawals, and records loan repayments |
| Accountant | Reviews ledgers, reconciles balances, and prepares financial reports |
| Auditor | Reviews transactions, approvals, and compliance records |
| Member | Views personal savings, welfare contributions, loans, and statements |

## Functional Requirements

### Member Management

- Register a new SACCO member.
- Assign each member to a branch.
- Search members by member number, name, phone, or ID number.
- Update member contact details.
- Change member status.
- View member savings, welfare, share capital, and loan history.

### Account Management

- Open one or more accounts for a member.
- Link each account to an account type and product.
- Prevent duplicate account numbers.
- View account balances.
- Generate account statements.
- Close or mark dormant accounts.

### Savings And Welfare

- Record member deposits.
- Record authorized withdrawals.
- Record monthly welfare contributions.
- Record share capital contributions.
- Support payroll deductions as a payment method.
- Generate member contribution reports.

### Loan Management

- Register loan applications.
- Capture requested amount, loan type, repayment period, and interest rate.
- Attach guarantors to the loan.
- Approve, reject, or cancel applications.
- Disburse approved loans.
- Track running, cleared, defaulted, and written-off loans.

### Loan Repayment

- Record loan repayments.
- Capture installment number.
- Split repayment into principal and interest.
- Track outstanding balance after each repayment.
- Support cash, bank transfer, mobile money, and payroll deduction.
- Generate arrears and repayment reports.

### Staff And Security

- Register staff.
- Assign staff to roles and branches.
- Restrict actions by role.
- Record the staff member who posts each transaction or repayment.
- Keep an audit trail for sensitive actions.

### Reports

- Member register
- Savings summary
- Welfare contribution report
- Share capital report
- Account statement
- Daily teller collection report
- Loan application report
- Loan portfolio report
- Loan arrears report
- Repayment report
- Branch performance report
- Audit report

## Screen Design

### Dashboard

- Total active members
- Total savings balance
- Total welfare fund balance
- Total share capital
- Active loans
- Loan arrears
- Today deposits
- Today repayments
- Recent transactions

### Members

Fields:

- Member number
- First name
- Middle name
- Last name
- Gender
- Date of birth
- ID number
- Phone
- Email
- Address
- Branch
- Date joined
- Status

Actions:

- Add member
- Edit member
- View profile
- Open account
- View statement
- View loans

### Accounts

Fields:

- Account number
- Member
- Account type
- Product
- Opening date
- Current balance
- Status

Actions:

- Open account
- Post deposit
- Post withdrawal
- View transactions
- Print statement

### Loans

Fields:

- Loan number
- Member
- Product
- Loan type
- Application date
- Approval date
- Loan amount
- Interest rate
- Repayment period
- Status
- Disbursement date

Actions:

- New application
- Add guarantors
- Approve loan
- Reject loan
- Disburse loan
- Record repayment
- View repayment history

### Guarantors

Fields:

- Guarantor member
- First name
- Last name
- ID number
- Phone
- Email
- Address
- Guaranteed amount

Actions:

- Add guarantor
- Link guarantor to loan
- Remove guarantor before approval

### Reports

Filters:

- Date from
- Date to
- Branch
- Member
- Product
- Loan type
- Status

Actions:

- View report
- Export to PDF
- Export to Excel
- Print

## Permissions Matrix

| Feature | Admin | Manager | Loans Officer | Teller | Accountant | Auditor |
| --- | --- | --- | --- | --- | --- | --- |
| Manage branches | Yes | View | No | No | View | View |
| Manage staff | Yes | View | No | No | No | View |
| Manage products | Yes | Yes | View | View | View | View |
| Register members | Yes | Yes | Yes | No | No | View |
| Open accounts | Yes | Yes | Yes | No | No | View |
| Post deposits | No | No | No | Yes | Yes | View |
| Post withdrawals | No | Approve | No | Yes | Yes | View |
| Register loan application | Yes | Yes | Yes | No | No | View |
| Approve loans | No | Yes | No | No | No | View |
| Disburse loans | No | Yes | No | No | Yes | View |
| Record repayments | No | No | No | Yes | Yes | View |
| View reports | Yes | Yes | Yes | Limited | Yes | Yes |

## Business Rules

- A member must be active before an account can be opened.
- A member must have at least one savings account before applying for a loan.
- A loan must have at least one guarantor before approval.
- Only a manager can approve or reject a loan.
- A loan cannot be disbursed before approval.
- A repayment cannot exceed the outstanding balance unless the overpayment policy allows it.
- A withdrawal cannot reduce an account below zero unless overdrafts are explicitly enabled.
- Every transaction must record the staff member who created it.
- Account balances must be updated in the same database transaction as the transaction record.

## Suggested Technology Stack

| Layer | Recommended Option |
| --- | --- |
| Database | Microsoft SQL Server |
| Backend | ASP.NET Core, Laravel, Django, or Node.js |
| Frontend | React, Vue, Angular, or server-rendered MVC |
| Authentication | Role-based login with password hashing |
| Reports | PDF and Excel export |
| Deployment | Local server, branch office server, or cloud-hosted system |

## Suggested Menu Structure

- Dashboard
- Members
- Accounts
- Transactions
- Loans
- Guarantors
- Repayments
- Staff
- Branches
- Products
- Reports
- Settings

