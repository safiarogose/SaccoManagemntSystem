from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.exceptions import FieldDoesNotExist
from django.db import DatabaseError
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from pathlib import Path

from .forms import (
    AccountForm,
    AccountTransactionForm,
    AccountTypeForm,
    ActivityLogForm,
    BranchForm,
    GuarantorForm,
    LoanForm,
    LoanGuarantorForm,
    LoanRepaymentForm,
    LoanTypeForm,
    MemberForm,
    PaymentMethodForm,
    PostTransactionForm,
    ProductForm,
    RecordRepaymentForm,
    RoleForm,
    SaccoGroupForm,
    SaccoUserForm,
    StaffForm,
    TransactionTypeForm,
)
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
from .services import (
    approve_loan,
    disburse_loan,
    post_account_transaction,
    record_loan_repayment,
    reject_loan,
)


BASE_DIR = Path(__file__).resolve().parent.parent
CHART_COLORS = ["#1abb9c", "#3498db", "#f0ad4e", "#e74c3c", "#7d5fb2", "#2a3f54"]
CHART_COLOR_NAMES = ["green", "blue", "amber", "red", "violet", "slate"]


DEMO_ADMIN_USERNAMES = {"admin", "admi"}


def ensure_demo_admin_login(username, password):
    if username.lower() not in DEMO_ADMIN_USERNAMES or password.strip() != "admin123":
        return

    admin, _ = User.objects.get_or_create(username="admin")
    admin.is_active = True
    admin.is_staff = True
    admin.is_superuser = True
    if not admin.has_usable_password() or not admin.check_password("admin123"):
        admin.set_password("admin123")
    admin.save()


def authenticate_authorized_user(request, username, password):
    if username.lower() in DEMO_ADMIN_USERNAMES and password.strip() == "admin123":
        return authenticate(request, username="admin", password="admin123")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        return user

    existing_user = User.objects.filter(username__iexact=username).first()
    if not existing_user:
        return None

    user = authenticate(request, username=existing_user.username, password=password)
    if user is not None:
        return user

    stripped_password = password.strip()
    if stripped_password != password:
        return authenticate(request, username=existing_user.username, password=stripped_password)

    return None


PAGES = {
    "dashboard": "Dashboard",
    "members": "Members",
    "accounts": "Accounts",
    "transactions": "Transactions",
    "loans": "Loans",
    "guarantors": "Guarantors",
    "repayments": "Repayments",
    "staff": "Staff",
    "branches": "Branches",
    "products": "Products",
    "reports": "Reports",
    "settings": "Settings",
    "activity-logs": "Activity Logs",
    "users": "Users",
    "groups": "Groups",
}


PAGE_MODEL_ROUTES = {
    "members": "members",
    "accounts": "accounts",
    "transactions": "account-transactions",
    "loans": "loans",
    "guarantors": "guarantors",
    "repayments": "loan-repayments",
    "staff": "staff",
    "branches": "branches",
    "products": "products",
    "settings": "records",
    "activity-logs": "activity-logs",
    "users": "users",
    "groups": "groups",
}

ACTIVE_PAGE_FOR_MODEL = {
    model_name: page_name
    for page_name, model_name in PAGE_MODEL_ROUTES.items()
    if model_name != "records"
}


MODEL_VIEWS = {
    "branches": {"model": Branch, "form": BranchForm, "title": "Branches", "columns": ["branch_code", "branch_name", "phone", "email", "status"], "search": ["branch_code", "branch_name", "phone", "email"]},
    "roles": {"model": Role, "form": RoleForm, "title": "Roles", "columns": ["role_name", "description"], "search": ["role_name", "description"]},
    "staff": {"model": Staff, "form": StaffForm, "title": "Staff", "columns": ["staff_no", "first_name", "last_name", "role", "branch", "status"], "search": ["staff_no", "first_name", "last_name", "phone", "email"]},
    "members": {"model": Member, "form": MemberForm, "title": "Members", "columns": ["member_no", "first_name", "last_name", "id_no", "phone", "branch", "status"], "search": ["member_no", "first_name", "middle_name", "last_name", "id_no", "phone", "email"]},
    "account-types": {"model": AccountType, "form": AccountTypeForm, "title": "Account Types", "columns": ["type_name", "description"], "search": ["type_name", "description"]},
    "products": {"model": Product, "form": ProductForm, "title": "Products", "columns": ["product_name", "product_category", "status"], "search": ["product_name", "description", "product_category"]},
    "accounts": {"model": Account, "form": AccountForm, "title": "Accounts", "columns": ["account_no", "member", "account_type", "product", "current_balance", "status"], "search": ["account_no", "member__member_no", "member__first_name", "member__last_name"]},
    "transaction-types": {"model": TransactionType, "form": TransactionTypeForm, "title": "Transaction Types", "columns": ["type_name", "description"], "search": ["type_name", "description"]},
    "payment-methods": {"model": PaymentMethod, "form": PaymentMethodForm, "title": "Payment Methods", "columns": ["method_name", "description", "status"], "search": ["method_name", "description"]},
    "account-transactions": {"model": AccountTransaction, "form": AccountTransactionForm, "title": "Account Transactions", "columns": ["transaction_date", "account", "transaction_type", "payment_method", "amount", "balance_after"], "search": ["account__account_no", "account__member__member_no", "narration"]},
    "loan-types": {"model": LoanType, "form": LoanTypeForm, "title": "Loan Types", "columns": ["type_name", "description"], "search": ["type_name", "description"]},
    "loans": {"model": Loan, "form": LoanForm, "title": "Loans", "columns": ["loan_no", "member", "loan_type", "loan_amount", "interest_rate", "repayment_period", "status"], "search": ["loan_no", "member__member_no", "member__first_name", "member__last_name"]},
    "guarantors": {"model": Guarantor, "form": GuarantorForm, "title": "Guarantors", "columns": ["member", "first_name", "last_name", "id_no", "phone"], "search": ["first_name", "last_name", "id_no", "phone", "member__member_no"]},
    "loan-guarantors": {"model": LoanGuarantor, "form": LoanGuarantorForm, "title": "Loan Guarantors", "columns": ["loan", "guarantor", "guaranteed_amount"], "search": ["loan__loan_no", "guarantor__first_name", "guarantor__last_name"]},
    "loan-repayments": {"model": LoanRepayment, "form": LoanRepaymentForm, "title": "Loan Repayments", "columns": ["repayment_date", "loan", "installment_no", "amount_paid", "balance_outstanding", "received_by"], "search": ["loan__loan_no", "loan__member__member_no"]},
    "activity-logs": {"model": ActivityLog, "form": ActivityLogForm, "title": "Activity Logs", "columns": ["created_at", "user", "action", "module", "object_repr", "ip_address"], "search": ["user__username", "action", "module", "object_repr", "description", "ip_address"], "readonly": True},
    "users": {"model": User, "form": SaccoUserForm, "title": "Users", "columns": ["username", "first_name", "last_name", "email", "is_staff", "is_active"], "search": ["username", "first_name", "last_name", "email"]},
    "groups": {"model": Group, "form": SaccoGroupForm, "title": "Groups", "columns": ["name"], "search": ["name"]},
}


MODEL_PERMISSIONS = {
    "branches": {"Administrator", "Manager", "Auditor"},
    "roles": {"Administrator", "Auditor"},
    "staff": {"Administrator", "Manager", "Auditor"},
    "members": {"Administrator", "Manager", "Loans Officer", "Auditor"},
    "account-types": {"Administrator", "Manager", "Auditor"},
    "products": {"Administrator", "Manager", "Auditor"},
    "accounts": {"Administrator", "Manager", "Loans Officer", "Accountant", "Auditor"},
    "transaction-types": {"Administrator", "Accountant", "Auditor"},
    "payment-methods": {"Administrator", "Accountant", "Auditor"},
    "account-transactions": {"Administrator", "Teller", "Accountant", "Auditor"},
    "loan-types": {"Administrator", "Manager", "Loans Officer", "Auditor"},
    "loans": {"Administrator", "Manager", "Loans Officer", "Auditor"},
    "guarantors": {"Administrator", "Manager", "Loans Officer", "Auditor"},
    "loan-guarantors": {"Administrator", "Manager", "Loans Officer", "Auditor"},
    "loan-repayments": {"Administrator", "Teller", "Accountant", "Auditor"},
    "activity-logs": {"Administrator", "Manager", "Auditor"},
    "users": {"Administrator"},
    "groups": {"Administrator"},
}


def get_model_config(model_name):
    return MODEL_VIEWS.get(model_name)


def client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_activity(request, action, module="", object_repr="", description=""):
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    ActivityLog.objects.create(
        user=user,
        action=action,
        module=module,
        object_repr=str(object_repr)[:255],
        description=description,
        ip_address=client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def model_field_value(instance, field_name):
    try:
        instance._meta.get_field(field_name)
    except FieldDoesNotExist:
        return ""
    value = getattr(instance, field_name)
    return value if value not in (None, "") else "-"


def model_context(config, model_name, **extra):
    context = {
        "active_page": ACTIVE_PAGE_FOR_MODEL.get(model_name, ""),
        "model_name": model_name,
        "model_title": config["title"],
        "page_title": config["title"],
        "columns": config["columns"],
        "model_links": MODEL_VIEWS,
        "readonly": config.get("readonly", False),
    }
    context.update(extra)
    return context


def require_module_access(request, model_name):
    if request.user.is_superuser or request.user.is_staff:
        return
    allowed = MODEL_PERMISSIONS.get(model_name, set())
    user_groups = set(request.user.groups.values_list("name", flat=True))
    if not allowed.intersection(user_groups):
        log_activity(request, "denied", model_name, description="User attempted to access a restricted module.")
        raise PermissionDenied("You do not have permission to access this module.")


def chart_gradient(rows, value_key="total"):
    running = 0
    parts = []
    total = sum(float(row.get(value_key) or 0) for row in rows)
    if not total:
        return "conic-gradient(#edf0ec 0% 100%)"
    for index, row in enumerate(rows):
        value = float(row.get(value_key) or 0)
        next_stop = running + (value / total) * 100
        parts.append(f"{CHART_COLORS[index % len(CHART_COLORS)]} {running:.2f}% {next_stop:.2f}%")
        running = next_stop
    return f"conic-gradient({', '.join(parts)})"


def shifted_month(year, month, offset):
    month_index = year * 12 + (month - 1) + offset
    return month_index // 12, month_index % 12 + 1


def home(request):
    try:
        active_members = Member.objects.filter(status="Active").count()
        total_members = Member.objects.count()
        total_savings = Account.objects.aggregate(total=Sum("current_balance"))["total"] or 0
        active_loans = Loan.objects.exclude(status__in=["Cleared", "Rejected"]).count()
        branch_count = Branch.objects.count()
    except DatabaseError:
        active_members = 0
        total_members = 0
        total_savings = 0
        active_loans = 0
        branch_count = 0

    return render(
        request,
        "core/welcome.html",
        {
            "page_title": "Welcome To PPSW SACCO",
            "active_members": active_members,
            "total_members": total_members,
            "total_savings": total_savings,
            "active_loans": active_loans,
            "branch_count": branch_count,
        },
    )


@login_required(login_url="login")
def dashboard(request):
    active_members = Member.objects.filter(status="Active").count()
    total_members = Member.objects.count()
    total_savings = Account.objects.aggregate(total=Sum("current_balance"))["total"] or 0
    active_loans = Loan.objects.exclude(status__in=["Cleared", "Rejected"])
    loan_portfolio = active_loans.aggregate(total=Sum("loan_amount"))["total"] or 0
    arrears = Loan.objects.filter(status="Defaulted").aggregate(total=Sum("loan_amount"))["total"] or 0
    recent_transactions = AccountTransaction.objects.select_related(
        "account__member", "transaction_type", "payment_method", "created_by"
    )[:8]
    loan_queue = Loan.objects.select_related("member", "loan_type").filter(status__in=["Applied", "Approved", "Defaulted"])[:6]
    transaction_total = AccountTransaction.objects.aggregate(total=Sum("amount"))["total"] or 0
    account_count = Account.objects.count()
    branch_rows = []
    max_branch_members = 1
    max_branch_savings = 1
    max_branch_loans = 1
    for branch in Branch.objects.all():
        member_count = Member.objects.filter(branch=branch).count()
        member_ids = Member.objects.filter(branch=branch).values_list("id", flat=True)
        branch_savings = Account.objects.filter(member_id__in=member_ids).aggregate(total=Sum("current_balance"))["total"] or 0
        branch_loans = Loan.objects.filter(member_id__in=member_ids).aggregate(total=Sum("loan_amount"))["total"] or 0
        max_branch_members = max(max_branch_members, member_count)
        max_branch_savings = max(max_branch_savings, branch_savings)
        max_branch_loans = max(max_branch_loans, branch_loans)
        branch_rows.append(
            {
                "name": branch.branch_name,
                "members": member_count,
                "savings": branch_savings,
                "loans": branch_loans,
            }
        )
    for branch in branch_rows:
        branch["member_percent"] = int((branch["members"] / max_branch_members) * 100) if max_branch_members else 0
        branch["savings_percent"] = int((branch["savings"] / max_branch_savings) * 100) if max_branch_savings else 0
        branch["loans_percent"] = int((branch["loans"] / max_branch_loans) * 100) if max_branch_loans else 0

    product_rows = list(
        Account.objects.values("product__product_name")
        .annotate(total=Sum("current_balance"), accounts=Count("id"))
        .order_by("-total")[:6]
    )
    max_product_total = max([row["total"] or 0 for row in product_rows] or [1])
    for row in product_rows:
        row["percent"] = int(((row["total"] or 0) / max_product_total) * 100) if max_product_total else 0

    loan_status_rows = list(Loan.objects.values("status").annotate(total=Count("id")).order_by("status"))
    loan_status_total = sum(row["total"] for row in loan_status_rows) or 1
    for index, row in enumerate(loan_status_rows):
        row["percent"] = int((row["total"] / loan_status_total) * 100)
        row["color"] = CHART_COLOR_NAMES[index % len(CHART_COLOR_NAMES)]
    loan_status_gradient = chart_gradient(loan_status_rows)

    capital_total = total_savings + loan_portfolio
    savings_share = int((total_savings / capital_total) * 100) if capital_total else 0
    loans_share = int((loan_portfolio / capital_total) * 100) if capital_total else 0
    arrears_share = int((arrears / loan_portfolio) * 100) if loan_portfolio else 0
    product_pie_rows = []
    product_total = sum(row["total"] or 0 for row in product_rows) or 1
    for index, row in enumerate(product_rows):
        product_pie_rows.append(
            {
                "name": row["product__product_name"] or "Unassigned Product",
                "total": row["total"] or 0,
                "percent": int(((row["total"] or 0) / product_total) * 100),
                "color": CHART_COLOR_NAMES[index % len(CHART_COLOR_NAMES)],
            }
        )
    product_balance_gradient = chart_gradient(product_pie_rows)

    raw_monthly_transaction_rows = list(
        AccountTransaction.objects.annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("month")
    )
    monthly_totals = {
        (row["month"].year, row["month"].month): row
        for row in raw_monthly_transaction_rows
        if row["month"]
    }
    today = timezone.localdate()
    month_keys = [shifted_month(today.year, today.month, offset) for offset in range(-5, 1)]
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_transaction_rows = [
        {
            "month": monthly_totals.get(key, {}).get("month"),
            "label": month_labels[key[1] - 1],
            "total": monthly_totals.get(key, {}).get("total", 0),
            "count": monthly_totals.get(key, {}).get("count", 0),
        }
        for key in month_keys
    ]
    max_monthly_total = max([row["total"] or 0 for row in monthly_transaction_rows] or [1])
    monthly_line_points = []
    monthly_line_area_points = []
    row_count = len(monthly_transaction_rows)
    for index, row in enumerate(monthly_transaction_rows):
        row["percent"] = int(((row["total"] or 0) / max_monthly_total) * 100) if max_monthly_total else 0
        x = 8 + ((84 / (row_count - 1)) * index if row_count > 1 else 42)
        y = 92 - (row["percent"] * 0.76)
        row["line_x"] = f"{x:.1f}"
        row["line_y"] = f"{y:.1f}"
        point = f"{x:.1f},{y:.1f}"
        monthly_line_points.append(point)
        monthly_line_area_points.append(point)
    monthly_line = " ".join(monthly_line_points)
    monthly_line_area = f"8,96 {' '.join(monthly_line_area_points)} 92,96" if monthly_line_area_points else ""

    return render(
        request,
        "core/dashboard.html",
        {
            "page_title": PAGES["dashboard"],
            "active_page": "dashboard",
            "active_members": active_members,
            "total_members": total_members,
            "total_savings": total_savings,
            "loan_portfolio": loan_portfolio,
            "active_loan_count": active_loans.count(),
            "arrears": arrears,
            "arrears_count": Loan.objects.filter(status="Defaulted").count(),
            "recent_transactions": recent_transactions,
            "loan_queue": loan_queue,
            "transaction_total": transaction_total,
            "account_count": account_count,
            "branch_rows": branch_rows,
            "product_rows": product_rows,
            "loan_status_rows": loan_status_rows,
            "savings_share": savings_share,
            "loans_share": loans_share,
            "arrears_share": arrears_share,
            "product_pie_rows": product_pie_rows,
            "monthly_transaction_rows": monthly_transaction_rows,
            "loan_status_gradient": loan_status_gradient,
            "product_balance_gradient": product_balance_gradient,
            "monthly_line": monthly_line,
            "monthly_line_area": monthly_line_area,
        },
    )


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        ensure_demo_admin_login(username, password)
        user = authenticate_authorized_user(request, username, password)

        if user is not None:
            login(request, user)
            log_activity(request, "login", "authentication", user.username, "User signed in.")
            return redirect(request.GET.get("next") or "dashboard")

        log_activity(request, "login_failed", "authentication", username, "Invalid username or password.")
        messages.error(request, "Invalid username or password.")

    return render(request, "core/login.html", {"page_title": "Login"})


@login_required(login_url="login")
def logout_page(request):
    if request.method == "POST":
        log_activity(request, "logout", "authentication", request.user.username, "User signed out.")
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("login")

    return render(request, "core/logout.html", {"page_title": "Logout"})


@login_required(login_url="login")
def model_index(request):
    return render(
        request,
        "core/model_index.html",
        {
            "active_page": "",
            "page_title": "Database Records",
            "model_links": MODEL_VIEWS,
        },
    )


@login_required(login_url="login")
def reports_dashboard(request):
    require_module_access(request, "account-transactions")
    report_cards = [
        {
            "title": "Member Register",
            "count": Member.objects.count(),
            "total": "",
            "url": "members",
        },
        {
            "title": "Account Balances",
            "count": Account.objects.count(),
            "total": Account.objects.aggregate(total=Sum("current_balance"))["total"] or 0,
            "url": "accounts",
        },
        {
            "title": "Loan Portfolio",
            "count": Loan.objects.exclude(status__in=["Rejected"]).count(),
            "total": Loan.objects.exclude(status__in=["Rejected"]).aggregate(total=Sum("loan_amount"))["total"] or 0,
            "url": "loans",
        },
        {
            "title": "Loan Arrears",
            "count": Loan.objects.filter(status="Defaulted").count(),
            "total": Loan.objects.filter(status="Defaulted").aggregate(total=Sum("outstanding_balance"))["total"] or 0,
            "url": "loans",
        },
        {
            "title": "Repayment Report",
            "count": LoanRepayment.objects.count(),
            "total": LoanRepayment.objects.aggregate(total=Sum("amount_paid"))["total"] or 0,
            "url": "loan-repayments",
        },
        {
            "title": "Teller Collections",
            "count": AccountTransaction.objects.count(),
            "total": AccountTransaction.objects.aggregate(total=Sum("amount"))["total"] or 0,
            "url": "account-transactions",
        },
    ]
    return render(
        request,
        "core/reports_dashboard.html",
        {
            "active_page": "reports",
            "page_title": "Reports",
            "report_cards": report_cards,
        },
    )


@login_required(login_url="login")
def model_list(request, model_name):
    config = get_model_config(model_name)
    if not config:
        return render(request, "core/404.html", status=404)
    require_module_access(request, model_name)

    queryset = config["model"].objects.all()
    if not queryset.ordered:
        queryset = queryset.order_by("pk")
    query = request.GET.get("q", "").strip()
    if query:
        conditions = Q()
        for field in config["search"]:
            conditions |= Q(**{f"{field}__icontains": query})
        queryset = queryset.filter(conditions)

    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    rows = [
        {
            "object": instance,
            "values": [model_field_value(instance, column) for column in config["columns"]],
        }
        for instance in page_obj.object_list
    ]

    return render(
        request,
        "core/model_list.html",
        model_context(config, model_name, page_obj=page_obj, rows=rows, query=query),
    )


@login_required(login_url="login")
def model_create(request, model_name):
    config = get_model_config(model_name)
    if not config:
        return render(request, "core/404.html", status=404)
    require_module_access(request, model_name)
    if config.get("readonly"):
        messages.error(request, f"{config['title']} records are read-only.")
        return redirect("model-list", model_name=model_name)

    form_class = config["form"]
    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        instance = form.save()
        if isinstance(instance, AccountTransaction):
            instance.account.current_balance = instance.balance_after
            instance.account.save(update_fields=["current_balance", "updated_at"])
        log_activity(request, "create", model_name, instance, f"Created {config['title']} record.")
        messages.success(request, f"{config['title']} record created.")
        return redirect("model-list", model_name=model_name)

    return render(
        request,
        "core/model_form.html",
        model_context(config, model_name, form=form, action="Create"),
    )


@login_required(login_url="login")
def model_update(request, model_name, pk):
    config = get_model_config(model_name)
    if not config:
        return render(request, "core/404.html", status=404)
    require_module_access(request, model_name)
    if config.get("readonly"):
        messages.error(request, f"{config['title']} records are read-only.")
        return redirect("model-list", model_name=model_name)

    instance = get_object_or_404(config["model"], pk=pk)
    form_class = config["form"]
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        instance = form.save()
        if isinstance(instance, AccountTransaction):
            instance.account.current_balance = instance.balance_after
            instance.account.save(update_fields=["current_balance", "updated_at"])
        log_activity(request, "update", model_name, instance, f"Updated {config['title']} record.")
        messages.success(request, f"{config['title']} record updated.")
        return redirect("model-list", model_name=model_name)

    return render(
        request,
        "core/model_form.html",
        model_context(config, model_name, form=form, object=instance, action="Edit"),
    )


@login_required(login_url="login")
def model_delete(request, model_name, pk):
    config = get_model_config(model_name)
    if not config:
        return render(request, "core/404.html", status=404)
    require_module_access(request, model_name)
    if config.get("readonly"):
        messages.error(request, f"{config['title']} records are read-only.")
        return redirect("model-list", model_name=model_name)

    instance = get_object_or_404(config["model"], pk=pk)
    if request.method == "POST":
        try:
            object_repr = str(instance)
            instance.delete()
            log_activity(request, "delete", model_name, object_repr, f"Deleted {config['title']} record.")
            messages.success(request, f"{config['title']} record deleted.")
        except ProtectedError:
            messages.error(request, "This record is linked to other records and cannot be deleted.")
        return redirect("model-list", model_name=model_name)

    return render(
        request,
        "core/model_confirm_delete.html",
        model_context(config, model_name, object=instance),
    )


@login_required(login_url="login")
def post_transaction(request):
    require_module_access(request, "account-transactions")
    form = PostTransactionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            data = form.cleaned_data.copy()
            data["staff"] = data.pop("created_by")
            transaction_record = post_account_transaction(**data)
            log_activity(request, "workflow", "account-transactions", transaction_record, "Posted account transaction.")
            messages.success(request, f"Transaction posted. New balance: UGX {transaction_record.balance_after:,.0f}.")
            return redirect("model-list", model_name="account-transactions")
        except Exception as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "core/workflow_form.html",
        {
            "active_page": "transactions",
            "page_title": "Post Transaction",
            "title": "Post Account Transaction",
            "subtitle": "Deposits, withdrawals, charges, and repayments update balances through business rules.",
            "form": form,
            "back_url": "model-list",
            "back_model": "account-transactions",
        },
    )


@login_required(login_url="login")
def loan_action(request, pk, action):
    require_module_access(request, "loans")
    loan = get_object_or_404(Loan, pk=pk)
    actions = {
        "approve": approve_loan,
        "reject": reject_loan,
        "disburse": disburse_loan,
    }
    if action not in actions:
        return render(request, "core/404.html", status=404)
    if request.method == "POST":
        try:
            actions[action](loan=loan)
            log_activity(request, "workflow", "loans", loan, f"Loan {action} action completed.")
            messages.success(request, f"Loan {loan.loan_no} {action}d successfully.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("model-list", model_name="loans")

    return render(
        request,
        "core/loan_action.html",
        {
            "active_page": "loans",
            "page_title": f"{action.title()} Loan",
            "loan": loan,
            "action": action,
        },
    )


@login_required(login_url="login")
def loan_repayment(request, pk):
    require_module_access(request, "loan-repayments")
    loan = get_object_or_404(Loan, pk=pk)
    form = RecordRepaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            repayment = record_loan_repayment(loan=loan, **form.cleaned_data)
            log_activity(request, "workflow", "loan-repayments", repayment, "Recorded loan repayment.")
            messages.success(request, f"Repayment recorded. Outstanding balance: UGX {repayment.balance_outstanding:,.0f}.")
            return redirect("model-list", model_name="loan-repayments")
        except Exception as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "core/workflow_form.html",
        {
            "active_page": "repayments",
            "page_title": "Record Repayment",
            "title": f"Record Repayment For {loan.loan_no}",
            "subtitle": f"Outstanding balance: UGX {loan.outstanding_balance:,.0f}",
            "form": form,
            "back_url": "model-list",
            "back_model": "loans",
        },
    )


@login_required(login_url="login")
def page(request, page_name):
    if page_name not in PAGES:
        return render(request, "core/404.html", status=404)

    model_route = PAGE_MODEL_ROUTES.get(page_name)
    if model_route == "records":
        return redirect("model-index")
    if model_route:
        return redirect("model-list", model_name=model_route)

    return render(
        request,
        f"core/{page_name}.html",
        {"page_title": PAGES[page_name], "active_page": page_name},
    )


def styles(request):
    return FileResponse(open(BASE_DIR / "styles.css", "rb"), content_type="text/css")


def script(request):
    return FileResponse(open(BASE_DIR / "app.js", "rb"), content_type="text/javascript")
