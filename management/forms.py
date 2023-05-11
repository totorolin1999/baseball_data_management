from django import forms
from .models import Cup, Player, Game, Team, Team_Cup, Team_Game, Team_Player, Batting, Pitching

class CupForm(forms.ModelForm):
    cup_name = forms.CharField(label="", help_text="", widget=forms.TextInput(attrs={'placeholder': '輸入盃賽名稱'}), required = True)
    class Meta:
        model = Cup
        fields = ['cup_name']

class PlayerForm(forms.ModelForm):
    player_name = forms.CharField(label="", help_text="", widget=forms.TextInput(attrs={'placeholder': '球員姓名'}), required = True)
    class Meta:
        model = Player
        fields = ['player_name']

class GameForm(forms.ModelForm):
    game_name = forms.CharField(label="", help_text="", widget=forms.TextInput(attrs={'placeholder': '輸入比賽名稱'}), required = True)
    class Meta:
        model = Game
        fields = ['game_name']

class TeamForm(forms.ModelForm):
    team_name = forms.CharField(label="", help_text="", widget=forms.TextInput(attrs={'placeholder': '輸入所屬球隊'}))
    class Meta:
        model = Team
        fields = ['team_name']

class Team_GameForm(forms.ModelForm):
    class Meta:
        model = Team_Game
        fields = ['team_role']

class Team_PlayerForm(forms.ModelForm):
    class Meta:
        model = Team_Player
        fields = []

class BattingForm(forms.ModelForm):
    b_pa = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '打席'}), required = True)
    b_single = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '一安'}), required = True)
    b_double = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '二安'}), required = True)
    b_triple = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '三安'}), required = True)
    b_hr = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '全壘打'}), required = True)
    b_rbi = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '打點'}), required = True)
    b_bb = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '四壞'}), required = True)
    b_ibb = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '故四'}), required = True)
    b_hbp = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '死球'}), required = True)
    b_so = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '三振'}), required = True)
    b_sh = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '犧短'}), required = True)
    b_sf = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '犧飛'}), required = True)

    class Meta:
        model = Batting
        fields = ['b_pa', 'b_single', 'b_double', 'b_triple', 'b_hr', 'b_rbi', 'b_bb', 'b_ibb', 'b_hbp', 'b_so', 'b_sh', 'b_sf']

class PitchingForm(forms.ModelForm):
    p_ip = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '局數'}), required = False)
    p_single = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '被一安'}), required = False)
    p_er = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '責失'}), required = False)
    p_double = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '被二安'}), required = False)
    p_triple = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '被三安'}), required = False)
    p_hr = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '被全壘打'}), required = False)
    p_bb = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '四壞'}), required = False)
    p_ibb = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '故四'}), required = False)
    p_hbp = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '死球'}), required = False)
    p_so = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '三振'}), required = False)
    p_sf = forms.IntegerField(label="", help_text="", widget=forms.NumberInput(attrs={'placeholder': '犧飛'}), required = False)

    class Meta:
        model = Pitching
        fields = ['p_ip', 'p_single', 'p_er', 'p_double', 'p_triple', 'p_hr', 'p_bb', 'p_ibb', 'p_hbp', 'p_so', 'p_sf']
