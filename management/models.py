from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Cup(models.Model):
    cup_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cup_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cup_name


class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    player_name = models.CharField(max_length=255)

    def __str__(self):
        return self.player_name


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)
    game_name = models.CharField(max_length=255)
    Battings = models.ManyToManyField(Player, through='Batting', related_name="Batting")
    Pitchings = models.ManyToManyField(Player, through='Pitching', related_name="Pitching")

    def __str__(self):
        return self.game_name


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)
    Cups = models.ManyToManyField(Cup, through='Team_Cup')
    Games = models.ManyToManyField(Game, through='Team_Game')
    Players = models.ManyToManyField(Player, through='Team_Player')

    def __str__(self):
        return self.team_name


class Team_Cup(models.Model):
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team.team_name} - {self.cup.cup_name}"


class Team_Game(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_role = models.CharField(max_length=255)
    ip_role = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.team.team_name} ({self.team_role}) in {self.game.game_name}"


class Team_Player(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player.player_name} ({self.team.team_name})"


class Batting(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_order = models.PositiveIntegerField(null=True)
    player_role = models.CharField(max_length=255)
    b_pa = models.PositiveIntegerField(default=0)
    b_single = models.PositiveIntegerField(default=0)
    b_double = models.PositiveIntegerField(default=0)
    b_triple = models.PositiveIntegerField(default=0)
    b_hr = models.PositiveIntegerField(default=0)
    b_rbi = models.PositiveIntegerField(default=0)
    b_bb = models.PositiveIntegerField(default=0)
    b_ibb = models.PositiveIntegerField(default=0)
    b_hbp = models.PositiveIntegerField(default=0)
    b_so = models.PositiveIntegerField(default=0)
    b_sh = models.PositiveIntegerField(default=0)
    b_sf = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.player_name} Batting in {self.game.game_name}"


class Pitching(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_order = models.PositiveIntegerField(null=True)
    player_role = models.CharField(max_length=255)
    p_ip = models.PositiveIntegerField(default=0)
    p_single = models.PositiveIntegerField(default=0)
    p_er = models.PositiveIntegerField(default=0)
    p_double = models.PositiveIntegerField(default=0)
    p_triple = models.PositiveIntegerField(default=0)
    p_hr = models.PositiveIntegerField(default=0)
    p_bb = models.PositiveIntegerField(default=0)
    p_ibb = models.PositiveIntegerField(default=0)
    p_hbp = models.PositiveIntegerField(default=0)
    p_so = models.PositiveIntegerField(default=0)
    p_sf = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.player_name} Pitching in {self.game.game_name}"
