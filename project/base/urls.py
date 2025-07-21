from django.urls import path
from . import views


urlpatterns = [
    path("service/", views.ServiceView.as_view(), name="service"),
    path("delete_service/<int:pk>/", views.DeleteService, name="delete_service"),
    path("edit_service/<int:pk>/", views.EditServiceView.as_view(), name="edit_service"),
    path("project/", views.ProjectView.as_view(), name="project"),
    path("delete_project/<int:pk>/", views.DeleteProject, name="delete_project"),
    path("edit_project/<int:pk>/", views.EditProjectView.as_view(), name="edit_project"),

    path("enquiry/", views.EnquiryView.as_view(), name="enquiry"),
    path('load_districts/', views.load_districts, name="load_districts"),
    path('follow_up/', views.FollowUpView.as_view(), name="follow_up"),
    path("view_enquiry/<int:pk>/", views.ViewEnquiry, name="view_enquiry"),
    path("edit_enquiry/<int:pk>/", views.EditEnquiryView.as_view(), name="edit_enquiry"),
    path("drop_enquiry/<int:pk>/", views.DropEnquiry, name="drop_enquiry"),
    path("add_follow_up/<int:pk>/", views.AddFollowUpView.as_view(), name="add_follow_up"),

    path('work_list/', views.WorkListView.as_view(), name="work_list"),
    path("view_work/<int:pk>/", views.ViewWork, name="view_work"),
    path("edit_work/<int:pk>/", views.EditWorkView.as_view(), name="edit_work"),
    path("assign_work/<int:pk>/", views.AssignWorkView.as_view(), name="assign_work"),
    path("add_payment/<int:pk>/", views.AddPaymentView.as_view(), name="add_payment"),
    path("update_status/<int:pk>/", views.UpdateWorkStatusView.as_view(), name="update_status"),
    path("add_payment_remark/<int:pk>/", views.AddPaymentRemarkView.as_view(), name="add_payment_remark"),
    path("drop_work/<int:pk>/", views.DropWork, name="drop_work"),

    path('completed_work_list/', views.CompletedWorkListView.as_view(), name="completed_work_list"),
    path("view_completed_work/<int:pk>/", views.ViewCompletedWork, name="view_completed_work"),
    path("work_payment/<int:pk>/", views.WorkPaymentView.as_view(), name="work_payment"),
    
    path('dropped_list/', views.DroppedListView.as_view(), name="dropped_list"),
    path("view_dropped/<int:pk>/", views.ViewDropped, name="view_dropped"),

    path('payments/', views.PaymentsView.as_view(), name="payments"),
    path('payment_due_list/', views.PaymentDueListView.as_view(), name="payment_due_list"),
    path('site_eng_status/', views.SiteEngStatusListView.as_view(), name="site_eng_status"),
    path('site_eng_status/<int:pk>/', views.SiteEngStatusView.as_view(), name="site_eng_status_view"),
]