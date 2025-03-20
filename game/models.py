from django.db import models
from django.contrib.auth.models import User

# Model to store country details, including the name and flag URL
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Unique country name with a max length of 100 characters
    flag_url = models.URLField()  # Stores the URL of the country's flag image

    def __str__(self):
        """
        String representation of the Country model.
        Returns the country name when the object is printed.
        """
        return self.name

# Model to store user scores in the game
class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links each score to a registered user
    score = models.IntegerField(default=0)  # Stores the user's score, default value is 0

    def __str__(self):
        """
        String representation of the Score model.
        Returns the username and their corresponding score when the object is printed.
        """
        return f"{self.user.username} - {self.score}"
