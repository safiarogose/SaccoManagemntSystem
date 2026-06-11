from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Branch(TimestampedModel):
    branch_code = models.CharField(max_length=30, unique=True)
    branch_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        ordering = ["branch_name"]

    def __str__(self):
        return self.branch_name


class Role(models.Model):
    role_name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["role_name"]

    def __str__(self):
        return self.role_name


class Staff(TimestampedModel):
    staff_no = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=1, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    date_hired = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        ordering = ["staff_no"]

    def __str__(self):
        return f"{self.staff_no} - {self.first_name} {self.last_name}"

class Member(models.Model):
    member_no = models.CharField(max_length=10, unique=True, blank=True)
    member_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if not self.member_no:
            last_member = Member.objects.order_by("id").last()

            if last_member and last_member.member_no:
                last_number = int(last_member.member_no.replace("M", ""))
                new_number = last_number + 1
            else:
                new_number = 1

            self.member_no = f"M{new_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_no} - {self.member_name}"

class AccountType(models.Model):
    type_name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["type_name"]

    def __str__(self):
        return self.type_name


class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    product_category = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        ordering = ["product_name"]

    def __str__(self):
        return self.product_name


class Account(TimestampedModel):
    account_no = models.CharField(max_length=40, unique=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    opening_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Active")
    current_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["account_no"]
        indexes = [
            models.Index(fields=["member"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.account_no} - {self.member}"


class TransactionType(models.Model):
    type_name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["type_name"]

    def __str__(self):
        return self.type_name


class PaymentMethod(models.Model):
    method_name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        ordering = ["method_name"]

    def __str__(self):
        return self.method_name


class AccountTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0.01)])
    balance_after = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    narration = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-transaction_date"]
        indexes = [models.Index(fields=["account", "transaction_date"])]

    def __str__(self):
        return f"{self.account} - {self.transaction_type} - {self.amount}"


class LoanType(models.Model):
    type_name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["type_name"]

    def __str__(self):
        return self.type_name


class Loan(TimestampedModel):
    loan_no = models.CharField(max_length=40, unique=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT)
    application_date = models.DateField(auto_now_add=True)
    approval_date = models.DateField(null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0.01)])
    outstanding_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    repayment_period = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="Applied")
    disbursement_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-application_date", "loan_no"]
        indexes = [
            models.Index(fields=["member"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.loan_no} - {self.member}"


class Guarantor(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    id_no = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class LoanGuarantor(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    guarantor = models.ForeignKey(Guarantor, on_delete=models.CASCADE)
    guaranteed_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["loan", "guarantor"]
        constraints = [
            models.UniqueConstraint(fields=["loan", "guarantor"], name="unique_loan_guarantor")
        ]

    def __str__(self):
        return f"{self.loan} guaranteed by {self.guarantor}"


class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    repayment_date = models.DateField(auto_now_add=True)
    installment_no = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0.01)])
    principal = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    interest = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    balance_outstanding = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    received_by = models.ForeignKey(Staff, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-repayment_date"]
        indexes = [models.Index(fields=["loan", "repayment_date"])]

    def __str__(self):
        return f"{self.loan} installment {self.installment_no}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("login_failed", "Failed Login"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("workflow", "Workflow"),
        ("denied", "Access Denied"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    module = models.CharField(max_length=80, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["module", "created_at"]),
        ]

    def __str__(self):
        actor = self.user.username if self.user else "System"
        return f"{actor} {self.action} {self.module}".strip()
