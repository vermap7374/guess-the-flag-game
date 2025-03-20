from django.urls import path
from .views import register_user, login_user, logout_user, game_view, leaderboard, home_view

# URL patterns for the game application
urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_user, name='register'),  # URL for user registration page
    path('login/', login_user, name='login'),  # URL for user login page
    path('logout/', logout_user, name='logout'),  # URL to log out the user
    path('game/', game_view, name='game'),  # URL to start/play the game
    path('leaderboard/', leaderboard, name='leaderboard'),  # URL to view the leaderboard
]
