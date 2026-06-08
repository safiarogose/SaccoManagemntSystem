from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountTransaction, LoanRepayment, TransactionType


MONEY_ZERO = Decimal("0.00")


def get_transaction_type(name):
    return TransactionType.objects.get(type_name=name)


@transaction.atomic
def post_account_transaction(*, account, transaction_type, payment_method, amount, narration, staff):
    amount = Decimal(amount)
    if amount <= MONEY_ZERO:
        raise ValidationError("Amount must be greater than zero.")
    if account.status != "Active":
        raise ValidationError("Only active accounts can receive transactions.")

    type_name = transaction_type.type_name
    sign = Decimal("-1") if type_name in {"Withdrawal", "Charge"} else Decimal("1")
    balance_after = account.current_balance + (sign * amount)
    if balance_after < MONEY_ZERO:
        raise ValidationError("Transaction blocked: account balance cannot go below zero.")

    account.current_balance = balance_after
    account.save(update_fields=["current_balance", "updated_at"])
    return AccountTransaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        payment_method=payment_method,
        amount=amount,
        balance_after=balance_after,
        narration=narration,
        created_by=staff,
    )


@transaction.atomic
def approve_loan(*, loan):
    if loan.status != "Applied":
        raise ValidationError("Only applied loans can be approved.")
    if not loan.loanguarantor_set.exists():
        raise ValidationError("A loan must have at least one guarantor before approval.")
    loan.status = "Approved"
    loan.approval_date = timezone.localdate()
    if loan.outstanding_balance <= MONEY_ZERO:
        loan.outstanding_balance = loan.loan_amount
    loan.save(update_fields=["status", "approval_date", "outstanding_balance", "updated_at"])
    return loan


@transaction.atomic
def reject_loan(*, loan):
    if loan.status not in {"Applied", "Approved"}:
        raise ValidationError("Only applied or approved loans can be rejected.")
    loan.status = "Rejected"
    loan.save(update_fields=["status", "updated_at"])
    return loan


@transaction.atomic
def disburse_loan(*, loan):
    if loan.status != "Approved":
        raise ValidationError("Only approved loans can be disbursed.")
    loan.status = "Running"
    loan.disbursement_date = timezone.localdate()
    if loan.outstanding_balance <= MONEY_ZERO:
        loan.outstanding_balance = loan.loan_amount
    loan.save(update_fields=["status", "disbursement_date", "outstanding_balance", "updated_at"])
    return loan


@transaction.atomic
def record_loan_repayment(*, loan, amount_paid, principal, interest, payment_method, received_by):
    amount_paid = Decimal(amount_paid)
    principal = Decimal(principal)
    interest = Decimal(interest)
    if loan.status not in {"Running", "Defaulted"}:
        raise ValidationError("Repayments can only be recorded against running or defaulted loans.")
    if amount_paid <= MONEY_ZERO:
        raise ValidationError("Repayment amount must be greater than zero.")
    if principal < MONEY_ZERO or interest < MONEY_ZERO:
        raise ValidationError("Principal and interest cannot be negative.")
    if principal + interest != amount_paid:
        raise ValidationError("Principal plus interest must equal amount paid.")
    if principal > loan.outstanding_balance:
        raise ValidationError("Principal repayment cannot exceed outstanding loan balance.")

    balance_outstanding = loan.outstanding_balance - principal
    installment_no = loan.loanrepayment_set.count() + 1
    repayment = LoanRepayment.objects.create(
        loan=loan,
        installment_no=installment_no,
        amount_paid=amount_paid,
        principal=principal,
        interest=interest,
        balance_outstanding=balance_outstanding,
        payment_method=payment_method,
        received_by=received_by,
    )
    loan.outstanding_balance = balance_outstanding
    loan.status = "Cleared" if balance_outstanding == MONEY_ZERO else "Running"
    loan.save(update_fields=["outstanding_balance", "status", "updated_at"])
    return repayment
