from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import (
    Account,
    AccountTransaction,
    AccountType,
    Branch,
    Loan,
    LoanType,
    Member,
    PaymentMethod,
    Product,
    Role,
    Staff,
    TransactionType,
)


class Command(BaseCommand):
    help = "Create demo data for the SACCO system."

    def handle(self, *args, **options):
        demo_password = "admin123"
        for username in ("admin", "safia"):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"is_staff": True, "is_superuser": True},
            )
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if created or not user.has_usable_password():
                user.set_password(demo_password)
            user.save()

        parliament, _ = Branch.objects.get_or_create(
            branch_code="BR-001",
            defaults={"branch_name": "Parliament Branch", "phone": "+256 700 000000", "status": "Active"},
        )
        central, _ = Branch.objects.get_or_create(
            branch_code="BR-002",
            defaults={"branch_name": "Central Branch", "phone": "+256 701 000000", "status": "Active"},
        )

        manager_role, _ = Role.objects.get_or_create(
            role_name="Manager",
            defaults={"description": "Approves loans and supervises SACCO operations"},
        )
        for role_name, description in [
            ("Administrator", "Manages users, roles, branches, and settings"),
            ("Loans Officer", "Processes loan applications and guarantors"),
            ("Teller", "Posts deposits, withdrawals, and repayments"),
            ("Accountant", "Reviews financial records and reports"),
            ("Auditor", "Reviews audit and compliance records"),
        ]:
            Role.objects.get_or_create(role_name=role_name, defaults={"description": description})

        staff, _ = Staff.objects.get_or_create(
            staff_no="STF-001",
            defaults={
                "first_name": "ROGOSE",
                "last_name": "SAFIA",
                "phone": "+256 700 000000",
                "email": "manager@ppsw.local",
                "role": manager_role,
                "branch": parliament,
                "status": "Active",
            },
        )

        savings_type, _ = AccountType.objects.get_or_create(type_name="Savings", defaults={"description": "Member savings account"})
        welfare_type, _ = AccountType.objects.get_or_create(type_name="Welfare", defaults={"description": "Member welfare account"})
        share_type, _ = AccountType.objects.get_or_create(type_name="Share Capital", defaults={"description": "Member share capital account"})

        ordinary, _ = Product.objects.get_or_create(
            product_name="Ordinary Savings",
            defaults={"description": "Regular member savings", "product_category": "Savings", "status": "Active"},
        )
        welfare, _ = Product.objects.get_or_create(
            product_name="Welfare Fund",
            defaults={"description": "Member welfare contribution", "product_category": "Savings", "status": "Active"},
        )
        normal_loan_product, _ = Product.objects.get_or_create(
            product_name="Normal Loan Product",
            defaults={"description": "Standard SACCO loan", "product_category": "Loan", "status": "Active"},
        )

        deposit_type, _ = TransactionType.objects.get_or_create(type_name="Deposit", defaults={"description": "Money paid into account"})
        repayment_type, _ = TransactionType.objects.get_or_create(type_name="Loan Repayment", defaults={"description": "Loan repayment received"})
        payroll, _ = PaymentMethod.objects.get_or_create(method_name="Payroll Deduction", defaults={"description": "Salary deduction", "status": "Active"})
        cash, _ = PaymentMethod.objects.get_or_create(method_name="Cash", defaults={"description": "Cash payment", "status": "Active"})

        normal_loan, _ = LoanType.objects.get_or_create(type_name="Normal Loan", defaults={"description": "Standard member loan"})
        emergency_loan, _ = LoanType.objects.get_or_create(type_name="Emergency Loan", defaults={"description": "Short term emergency loan"})

        safia, _ = Member.objects.get_or_create(
            member_no="PPSW-1183",
            defaults={
                "first_name": "ROGOSE",
                "last_name": "SAFIA",
                "id_no": "CM920114",
                "phone": "+256 700 000000",
                "address": "Parliament duty station",
                "status": "Active",
                "branch": parliament,
            },
        )
        amina, _ = Member.objects.get_or_create(
            member_no="PPSW-1184",
            defaults={
                "first_name": "AMINA",
                "last_name": "KATO",
                "id_no": "CM87012459",
                "phone": "+256 772 118400",
                "address": "Parliament duty station",
                "status": "Active",
                "branch": central,
            },
        )

        safia_account, _ = Account.objects.get_or_create(
            account_no="SA-001183",
            defaults={"account_type": savings_type, "member": safia, "product": ordinary, "current_balance": Decimal("7450000"), "status": "Active"},
        )
        amina_account, _ = Account.objects.get_or_create(
            account_no="WF-001184",
            defaults={"account_type": welfare_type, "member": amina, "product": welfare, "current_balance": Decimal("2150000"), "status": "Active"},
        )
        Account.objects.get_or_create(
            account_no="SC-001185",
            defaults={"account_type": share_type, "member": safia, "product": ordinary, "current_balance": Decimal("5300000"), "status": "Active"},
        )

        Loan.objects.get_or_create(
            loan_no="LN-2026-014",
            defaults={
                "member": safia,
                "product": normal_loan_product,
                "loan_type": normal_loan,
                "loan_amount": Decimal("5000000"),
                "outstanding_balance": Decimal("3820000"),
                "interest_rate": Decimal("12"),
                "repayment_period": 24,
                "status": "Running",
            },
        )
        Loan.objects.get_or_create(
            loan_no="LN-2026-015",
            defaults={
                "member": amina,
                "product": normal_loan_product,
                "loan_type": emergency_loan,
                "loan_amount": Decimal("1200000"),
                "outstanding_balance": Decimal("1200000"),
                "interest_rate": Decimal("10"),
                "repayment_period": 6,
                "status": "Applied",
            },
        )

        AccountTransaction.objects.get_or_create(
            account=safia_account,
            transaction_type=deposit_type,
            amount=Decimal("250000"),
            defaults={"payment_method": payroll, "balance_after": safia_account.current_balance, "narration": "Monthly contribution", "created_by": staff},
        )
        AccountTransaction.objects.get_or_create(
            account=amina_account,
            transaction_type=repayment_type,
            amount=Decimal("180000"),
            defaults={"payment_method": cash, "balance_after": amina_account.current_balance, "narration": "Installment payment", "created_by": staff},
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready. Login with admin / admin123 or safia / admin123."))
