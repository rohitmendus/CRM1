from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('accounts/login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html', 
            redirect_authenticated_user=True),
        name="login"),
    path('accounts/logout/',
        auth_views.LogoutView.as_view(),
        name="logout"),
    # path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('dashboard/', views.DashboardView.as_view(), name="dashboard"),
    path('sse/dasboard/', views.sse_dashboard, name="sse_dashboard"),
    path("dashboard/int_graph/", views.get_int_graph, name="int_graph"),
    
    path('users/', views.UserManagementView.as_view(), name="users"),
    path('edit_user/<int:pk>/', views.EditUserView.as_view(), name="edit_user"),
    path('drop_user/<int:pk>/', views.DropUser, name="drop_user"),
]
