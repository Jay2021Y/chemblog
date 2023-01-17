from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.utils import timezone


class DynamicContextLoginView(auth_views.LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time'] = timezone.now()
        return context


app_name = 'common'

urlpatterns = [
    path('naverlogin_reprompt', views.naverlogin_reprompt, name='naverlogin_reprompt'),
    path('signup_naver/<str:access_token>/', views.signup_naver, name='signup_naver'),
    path('naverlogin/', views.naverlogin, name='naverlogin'),
    path('navercallback/', views.navercallback, name='navercallback'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('signup_kakao/<str:access_token>/', views.signup_kakao, name='signup_kakao'),
    path('login/', DynamicContextLoginView.as_view(template_name='common/login.html'), name='login'),
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
