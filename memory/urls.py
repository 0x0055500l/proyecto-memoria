from django.urls import path
from . import views
from django.views.generic.base import RedirectView

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
]
