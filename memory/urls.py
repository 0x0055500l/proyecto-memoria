from django.urls import path
from . import views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('game/<str:difficulty>/', views.memory_game_view, name='game'),
    path('save-game/', views.save_game_view, name='save_game'),
    # Redirige /game/ (sin dificultad) a la selección de nivel (home)
    path('game/', RedirectView.as_view(pattern_name='home', permanent=False)),
    path('ranking/', views.ranking_view, name='ranking'),
    # --- RUTAS PARA RESET PASSWORD ---
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset_form.html',       # La página para hacer reset
             html_email_template_name='password_reset_email.html', # El *contenido* del correo
             subject_template_name='password_reset_subject.txt' # El *asunto* del correo
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html' # "Te hemos enviado un correo"
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html' # La página de nueva password
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html' # "Tu contraseña se cambió con éxito"
         ),
         name='password_reset_complete'),
]
