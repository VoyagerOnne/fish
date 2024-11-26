from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('/', HomeView.as_view(), name='home'),
    path('home/', HomeView.as_view(), name='home'),
    path('add_employee/', add_employee, name='add_employee'),
    path('employee/list/', EmployeeListView.as_view(), name='employee_list'),
    path('employee/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    path('add_test/', PhishingTestCreateView.as_view(), name='add_test'),
    path('created_tests/', PhishingTestListView.as_view(), name='created_tests'),
    path('test/detail/<int:pk>/', PhishingTestDetailView.as_view(), name='test_detail'),
    path('test/delete/<int:pk>/', PhishingTestDeleteView.as_view(), name='test_delete'),
    path('email_template/list/', PhishingEmailTemplateListView.as_view(), name='email_template_list'),
    path('email_template/create/', PhishingEmailTemplateCreateView.as_view(), name='email_template_create'),
    path('email_template/templates/', PhishingEmailTemplateListView.as_view(), name='email_templates_list'),
    path('email_template/templates/<int:pk>/', PhishingEmailTemplateDetailView.as_view(), name='email_template_detail'),
    path('email_template/delete/<int:pk>/', PhishingEmailTemplateDeleteView.as_view(), name='email_template_delete'),

    path('phishing_test/<int:test_id>/track/<int:employee_id>/<str:token>/', track_link, name='track_link'),
    path('phishing_test/<int:test_id>/track_open/<int:employee_id>/', track_open_email, name='track_open_email'),
    path('fake_login/<int:test_id>/<int:employee_id>/', fake_login_page, name='fake_login_page'),
    path('start_test/<int:test_id>/', start_phishing_test, name='start_phishing_test'),
    path('stop_test/<int:test_id>/', stop_phishing_test, name='stop_phishing_test'),

    path('campaign_results/<int:test_id>/', campaign_results_view, name='campaign_results'),
    path('export_csv/<int:test_id>/', export_csv, name='export_csv'),
]
