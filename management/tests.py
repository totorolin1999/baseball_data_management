from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Cup, Player, Game, Team, Team_Game, Batting, Pitching
from .views import calculate_batting_stats, calculate_pitching_stats


class StatCalculationTests(TestCase):
    def test_zero_batting_stats(self):
        stats = calculate_batting_stats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(stats['avg'], '0.000')
        self.assertEqual(stats['obp'], '0.000')
        self.assertEqual(stats['slg'], '0.000')
        self.assertEqual(stats['ops'], '0.000')

    def test_normal_batting_stats(self):
        # 10 PA, 1 BB -> 9 AB, 4 H (2 single, 1 double, 1 hr) -> 8 TB
        # AVG = 4/9 = 0.444, SLG = 8/9 = 0.889, OBP = 5/10 = 0.500
        stats = calculate_batting_stats(10, 2, 1, 0, 1, 1, 0, 0, 2, 0, 0)
        self.assertEqual(stats['avg'], '0.444')
        self.assertEqual(stats['obp'], '0.500')
        self.assertEqual(stats['slg'], '0.889')

    def test_zero_pitching_stats(self):
        stats = calculate_pitching_stats(0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(stats['era'], '0.000')
        self.assertEqual(stats['whip'], '0.000')

    def test_normal_pitching_stats(self):
        # 9 IP, 2 ER, 4 singles, 1 double, 1 hr, 2 BB, 8 SO
        # ERA = 2*9/9 = 2.000, WHIP = (6+2)/9 = 0.889
        stats = calculate_pitching_stats(9, 4, 1, 0, 1, 2, 8, 2)
        self.assertEqual(stats['era'], '2.000')
        self.assertEqual(stats['whip'], '0.889')
        self.assertEqual(stats['so9'], '8.000')


class ModelStrTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testmanager', password='password123')
        self.cup = Cup.objects.create(cup_name='春季聯賽', user=self.user)
        self.game = Game.objects.create(cup=self.cup, game_name='冠軍賽')
        self.team = Team.objects.create(team_name='猛瑪象', user=self.user)
        self.player = Player.objects.create(player_name='測試選手')

    def test_str_methods(self):
        self.assertEqual(str(self.cup), '春季聯賽')
        self.assertEqual(str(self.game), '冠軍賽')
        self.assertEqual(str(self.team), '猛瑪象')
        self.assertEqual(str(self.player), '測試選手')


class ViewAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testmanager', password='password123')

    def test_login_required_redirects(self):
        response = self.client.get(reverse('cup'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_authenticated_dashboard_access(self):
        self.client.login(username='testmanager', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
