from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import random
from .models import Country, Score
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model


# Get the User model dynamically (useful for custom user models)
User = get_user_model()

# Home View: Displays the homepage of the game
# This page serves as the entry point for users.
def home_view(request):
    return render(request, "game/home.html")

# Register User: Handles user registration, saving new users, and logging them in
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # Create form with POST data
        if form.is_valid():  # Validate form data
            user = form.save()  # Save new user to the database
            login(request, user)  # Automatically log in the new user
            return redirect('home')  # Redirect to home page after registration
    else:
        form = UserCreationForm()  # Initialize an empty registration form
    return render(request, 'game/register.html', {'form': form})

# Login User: Handles user authentication and login process
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # Create login form with submitted data
        if form.is_valid():  # Validate login credentials
            user = form.get_user()  # Retrieve authenticated user
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home after login
    else:
        form = AuthenticationForm()  # Display an empty login form
    return render(request, 'game/login.html', {'form': form})

# Logout User: Logs out the currently logged-in user and redirects to home
def logout_user(request):
    logout(request)  # Logs out the current user
    return redirect('home')  # Redirect back to the home page

# Game View: Handles the main game logic, including session management and user input
@login_required(login_url='login')  # Ensures only logged-in users can access the game
def game_view(request):
    countries = list(Country.objects.all())  # Fetch all available countries from the database
    
    if len(countries) < 4:
        return render(request, 'game/game.html', {'error': "Not enough countries in the database. Run 'import_countries'."})
    
    # Initialize session variables only if they are missing (prevents reset on reload)
    if 'lives' not in request.session:
        request.session['lives'] = 3  # Start with 3 lives
        request.session['score'] = 0  # Start with 0 score

    # Store the correct answer persistently to maintain game state
    if 'correct_country' not in request.session:
        correct_country = random.choice(countries)  # Randomly select a country as the correct answer
        request.session['correct_country'] = correct_country.name  # Store the correct country in session
    else:
        correct_country = Country.objects.get(name=request.session['correct_country'])  # Retrieve correct answer

    # Generate multiple-choice options (keep correct answer in the choices)
    choices = random.sample([c for c in countries if c.name != correct_country.name], 3)  # Select 3 incorrect options
    choices.append(correct_country)  # Add correct country to the choices
    random.shuffle(choices)  # Randomize answer order

    # Handle user input when a choice is submitted
    if request.method == "POST":
        selected_country = request.POST.get("choice", None)  # Retrieve user's selected answer
        correct_answer = request.session['correct_country']  # Retrieve correct answer from session

        # Handle timeout case (if user does not select an option)
        if selected_country == "timeout":
            request.session['lives'] -= 1  # Deduct a life for timeout
        elif selected_country == correct_answer:
            request.session['score'] += 10  # Increase score if answer is correct
        else:
            request.session['lives'] -= 1  # Deduct a life for incorrect answer

        # Reset correct answer for the next round
        request.session.pop('correct_country', None)

        # If lives reach 0, save score and end the game
        if request.session['lives'] <= 0:
            score, created = Score.objects.get_or_create(user=request.user)  # Get or create score entry for user
            if request.session['score'] > score.score:  # Update if the new score is higher
                score.score = request.session['score']
                score.save()

            # Reset game session variables (without logging the user out)
            request.session.pop('score', None)
            request.session.pop('lives', None)
            request.session.pop('correct_country', None)
            return redirect('leaderboard')  # Redirect to leaderboard after game over

        return redirect('game')  # Redirect back to game to load the next question

    return render(request, 'game/game.html', {
        'correct_country': correct_country,
        'choices': choices,
        'lives': request.session['lives'],
        'score': request.session['score']
    })

# Leaderboard View: Displays the top 10 highest scores
def leaderboard(request):
    top_players = Score.objects.select_related("user").order_by("-score")[:10]  # Fetch top 10 scores
    return render(request, "game/leaderboard.html", {"players": top_players})  # Render leaderboard page