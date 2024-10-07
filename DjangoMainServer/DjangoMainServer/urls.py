from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
#from .ContentProcessingNinja import TextAPI
#from .AudioFileManagementNinja import AudioAPI


urlpatterns = [
    path('admin/', admin.site.urls),
    #re_path('signup', views.signup),
    #re_path('login', views.login),
    #re_path('test_token', views.test_token),
    #re_path('logout', views.logout),
    #path("cpapi/", TextAPI.urls),
    #path("manageAudio/", include("TTSAudioFileManagement.urls")),
    path("authenticate/", include("SignInSystem.urls")),
    #path("manageAudio/", AudioAPI.urls),
    path("apis/", include("NinjaAPIs.urls")),

    #email password reset built in
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

