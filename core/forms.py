from django import forms
from django.contrib.auth.models import Group, User

from .models import (
    Account,
    AccountTransaction,
    AccountType,
    ActivityLog,
    Branch,
    Guarantor,
    Loan,
    LoanGuarantor,
    LoanRepayment,
    LoanType,
    Member,
    PaymentMethod,
    Product,
    Role,
    Staff,
    TransactionType,
)


class DateInputMixin:
    date_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.date_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.DateInput(attrs={"type": "date"})


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["branch_code", "branch_name", "address", "phone", "email", "status"]


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["role_name", "description"]


class StaffForm(DateInputMixin, forms.ModelForm):
    date_fields = ("date_hired",)

    class Meta:
        model = Staff
        fields = ["staff_no", "first_name", "last_name", "gender", "phone", "email", "role", "branch", "date_hired", "status"]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "id_no",
            "phone",
            "email",
            "address",
            "status",
            "branch",
        ]

class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ["type_name", "description"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_name", "description", "product_category", "status"]


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["account_no", "account_type", "member", "product", "status", "current_balance"]


class TransactionTypeForm(forms.ModelForm):
    class Meta:
        model = TransactionType
        fields = ["type_name", "description"]


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ["method_name", "description", "status"]


class AccountTransactionForm(forms.ModelForm):
    class Meta:
        model = AccountTransaction
        fields = ["account", "transaction_type", "payment_method", "amount", "balance_after", "narration", "created_by"]


class LoanTypeForm(forms.ModelForm):
    class Meta:
        model = LoanType
        fields = ["type_name", "description"]


class LoanForm(DateInputMixin, forms.ModelForm):
    date_fields = ("approval_date", "disbursement_date")

    class Meta:
        model = Loan
        fields = [
            "loan_no",
            "member",
            "product",
            "loan_type",
            "approval_date",
            "loan_amount",
            "outstanding_balance",
            "interest_rate",
            "repayment_period",
            "status",
            "disbursement_date",
        ]


class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = ["member", "first_name", "last_name", "id_no", "phone", "email", "address"]


class LoanGuarantorForm(forms.ModelForm):
    class Meta:
        model = LoanGuarantor
        fields = ["loan", "guarantor", "guaranteed_amount"]


class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanRepayment
        fields = [
            "loan",
            "installment_no",
            "amount_paid",
            "principal",
            "interest",
            "balance_outstanding",
            "payment_method",
            "received_by",
        ]


class PostTransactionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.filter(status="Active"))
    transaction_type = forms.ModelChoiceField(queryset=TransactionType.objects.all())
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.filter(status="Active"), required=False)
    amount = forms.DecimalField(min_value=0.01, max_digits=18, decimal_places=2)
    narration = forms.CharField(max_length=255, required=False)
    created_by = forms.ModelChoiceField(queryset=Staff.objects.filter(status="Active"))


class RecordRepaymentForm(forms.Form):
    amount_paid = forms.DecimalField(min_value=0.01, max_digits=18, decimal_places=2)
    principal = forms.DecimalField(min_value=0, max_digits=18, decimal_places=2)
    interest = forms.DecimalField(min_value=0, max_digits=18, decimal_places=2)
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.filter(status="Active"))
    received_by = forms.ModelChoiceField(queryset=Staff.objects.filter(status="Active"))


class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = []


class SaccoUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "groups", "is_staff", "is_active", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class SaccoGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "permissions"]
