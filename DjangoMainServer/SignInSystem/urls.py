from django.urls import path, re_path, include
from . import views

urlpatterns = [
     re_path('signup', views.signup),
     re_path('login', views.login),
     re_path('test_token', views.test_token),
     re_path('logout', views.logout),
     #path('changepassword/', views.ChangePassword.as_view(), name='changepassword'),
     #path('deleteuser/', views.DeleteUserAccount.as_view(), name='deleteuser'),
     path('change_password', views.change_password),
     path('delete_account', views.delete_account),
]
