from django.urls import include, path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('api/v1/rest-auth/', include('rest_auth.urls')),
    path('api/v1/rest-auth/registration/',
         views.AdminUserRegister.as_view(), name='register_user'),
    url(r'account-confirm-email/(?P<key>[-:\w]+)/$', views.null_view, name='account_confirm_email'),
    path('api/v1/rest-auth/registration/account-email-verification-sent/',
         views.null_view, name='account_email_verification_sent'),    
    path('api/v1/admin_users/',
         views.AdminUserList.as_view(), name='list_users'),
]
