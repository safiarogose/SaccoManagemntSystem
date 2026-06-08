from django.contrib import admin

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


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("branch_code", "branch_name", "phone", "status")
    search_fields = ("branch_code", "branch_name")
    list_filter = ("status",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("member_no", "first_name", "last_name", "branch", "phone", "status")
    search_fields = ("member_no", "first_name", "last_name", "id_no", "phone")
    list_filter = ("branch", "status")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_no", "member", "product", "account_type", "current_balance", "status")
    search_fields = ("account_no", "member__member_no", "member__first_name", "member__last_name")
    list_filter = ("account_type", "product", "status")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_no", "member", "loan_type", "loan_amount", "interest_rate", "repayment_period", "status")
    search_fields = ("loan_no", "member__member_no", "member__first_name", "member__last_name")
    list_filter = ("loan_type", "status")


admin.site.register(Role)
admin.site.register(Staff)
admin.site.register(AccountType)
admin.site.register(Product)
admin.site.register(TransactionType)
admin.site.register(PaymentMethod)
admin.site.register(AccountTransaction)
admin.site.register(LoanType)
admin.site.register(Guarantor)
admin.site.register(LoanGuarantor)
admin.site.register(LoanRepayment)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module", "object_repr", "ip_address")
    search_fields = ("user__username", "action", "module", "object_repr", "description", "ip_address")
    list_filter = ("action", "module", "created_at")
    readonly_fields = ("user", "action", "module", "object_repr", "description", "ip_address", "user_agent", "created_at")
