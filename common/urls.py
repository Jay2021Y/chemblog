from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path('user_profile/', views.user_profile, name='user_profile'),
    path('signup_kakao/<str:access_token>/', views.signup_kakao, name='signup_kakao'),
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('kakaologin/', views.kakaologin, name='kakaologin'),
    path('kakaocallback/', views.kakaocallback, name='kakaocallback'),
    path('logout/', auth_views.LogoutView.as_view(template_name='chemblog/index.html'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        email_template_name='common/password_reset_email.html', success_url='done'
    ),
        name='password_reset'
         ),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url='http://localhost:8000/common/password_reset_complete/'
    ),
         name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
