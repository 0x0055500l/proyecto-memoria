from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_victories = models.PositiveIntegerField(default=0)
    total_defeats = models.PositiveIntegerField(default=0)
    games_played = models.PositiveIntegerField(default=0)
    best_score = models.IntegerField(default=0)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Estadísticas de {self.user.username}"

class MemoryGame(models.Model):
    DIFFICULTY_CHOICES = [
        ('B', 'Básico'),
        ('M', 'Medio'),
        ('A', 'Avanzado'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES)
    moves = models.IntegerField(default=0)
    fails = models.IntegerField(default=0)
    time_spent = models.PositiveIntegerField()
    is_win = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Partida de Memory de {self.player.user.username}"
