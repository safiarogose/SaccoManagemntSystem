from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("welcome/", views.home, name="welcome"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("reports/", views.reports_dashboard, name="reports"),
    path("records/", views.model_index, name="model-index"),
    path("records/<str:model_name>/", views.model_list, name="model-list"),
    path("records/<str:model_name>/new/", views.model_create, name="model-create"),
    path("records/<str:model_name>/<int:pk>/edit/", views.model_update, name="model-update"),
    path("records/<str:model_name>/<int:pk>/delete/", views.model_delete, name="model-delete"),
    path("workflows/transactions/post/", views.post_transaction, name="post-transaction"),
    path("workflows/loans/<int:pk>/repayment/", views.loan_repayment, name="loan-repayment"),
    path("workflows/loans/<int:pk>/<str:action>/", views.loan_action, name="loan-action"),
    path("<str:page_name>/", views.page, name="page"),
    path("styles.css", views.styles, name="styles"),
    path("app.js", views.script, name="script"),
]
