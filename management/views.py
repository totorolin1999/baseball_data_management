from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Cup, Player, Game, Team, Team_Cup, Team_Game, Team_Player, Batting, Pitching
from .forms import CupForm, PlayerForm, GameForm, TeamForm, Team_GameForm, Team_PlayerForm, BattingForm, PitchingForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.


@login_required
def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def team(request):
    return render(request, 'dashboard/team.html')

@login_required
def hometeam(request):
    teamvalues = Team.objects.filter(user_id=request.user.id)
    team_gamevalues = Team_Game.objects.filter(team_role="hometeam")

    context = {
        'teamvalues': teamvalues,
        'team_gamevalues': team_gamevalues,
    }
    return render(request, 'dashboard/hometeam.html', context)

@login_required
def awayteam(request):
    teamvalues = Team.objects.filter(user_id=request.user.id)
    team_gamevalues = Team_Game.objects.filter(team_role="awayteam")

    context = {
        'teamvalues': teamvalues,
        'team_gamevalues': team_gamevalues,
    }
    return render(request, 'dashboard/awayteam.html', context)

@login_required
def hometeam_delete(request, team_id):
    hometeamvalue = Team.objects.get(team_id=team_id)
    if request.method == 'POST':
        hometeamvalue.delete()
        return redirect('hometeam')
    return render(request, 'dashboard/hometeam_delete.html')

@login_required
def hometeam_update(request, team_id):
    hometeamvalue = Team.objects.get(team_id=team_id)
    team_name1 = hometeamvalue.team_name
    if request.method == 'POST':
        hometeamform = TeamForm(request.POST, instance=hometeamvalue)
        if hometeamform.is_valid():
            hometeamform.save()
            team_name2 = hometeamvalue.team_name
            messages.success(request, f'您已成功將「{team_name1}」的球隊名稱修改為「{team_name2}」')
            return redirect('hometeam')
    else:
        hometeamform = TeamForm(instance=hometeamvalue)
    context = {
        'hometeamform': hometeamform,
    }
    return render(request, 'dashboard/hometeam_update.html', context)

@login_required
def cup(request):

    cupvalues = Cup.objects.filter(user_id=request.user.id).order_by('-cup_id')

    if request.method == 'POST':
        cupform = CupForm(request.POST)

        if cupform.is_valid():
            cupobj = cupform.save(commit=False)
            cupobj.user = request.user
            cupobj.save()
            cup_name = cupobj.cup_name
            messages.success(request, f'您已成功新增「{cup_name}」的盃賽記錄')
            return redirect('cup')
    else:
        cupform = CupForm()
    context = {
        'cupform': cupform,
        'cupvalues': cupvalues,
    }
    return render(request, 'dashboard/cup.html', context)

@login_required
def cup_delete(request, cup_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    cup_name = cupvalue.cup_name
    if request.method == 'POST':
        cupvalue.delete()
        messages.success(request, f'您已成功刪除「{cup_name}」的盃賽記錄')
        return redirect('cup')
    return render(request, 'dashboard/cup_delete.html')

@login_required
def cup_update(request, cup_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    cup_name1 = cupvalue.cup_name
    if request.method == 'POST':
        cupform = CupForm(request.POST, instance=cupvalue)
        if cupform.is_valid():
            cupform.save()
            cup_name2 = cupvalue.cup_name
            messages.success(request, f'您已成功將「{cup_name1}」的比賽名稱修改為「{cup_name2}」')
            return redirect('cup')
    else:
        cupform = CupForm(instance=cupvalue)
    context = {
        'cupform': cupform,
    }
    return render(request, 'dashboard/cup_update.html', context)

def saveTG(team_id,game_id,team_role):
    team_gameform = Team_GameForm()
    team_gameobj = team_gameform.save(commit=False)
    team_gameobj.team_id = team_id
    team_gameobj.game_id = game_id
    team_gameobj.team_role = team_role
    team_gameobj.save()

@login_required
def game(request, cup_id):

    cupvalue = Cup.objects.get(cup_id=cup_id)
    gamevalues = Game.objects.filter(cup_id=cup_id)
    hometeam_gamevalues = Team_Game.objects.filter(team_role="hometeam")
    awayteam_gamevalues = Team_Game.objects.filter(team_role="awayteam")
    # teamvalues = Team.objects.filter(Cups=cup_id)
    # for gamevalue in gamevalues:
    #     for hometeamvalue in hometeam_gamevalues.filter(game_id=gamevalue.game_id):
    #         print(hometeamvalue.team.team_name)
        # print(gamevalue.game_name)
        # for teamvalue in teamvalues:
        #     if teamvalue.Games.filter(game_id=gamevalue.game_id).exists():
        #         print(teamvalue.team_name)

    if request.method == 'POST':
        gameform = GameForm(request.POST)
        hometeam = request.POST.get('hometeam')
        awayteam = request.POST.get('awayteam')
        team_names=[hometeam, awayteam]

        if gameform.is_valid():
            gameobj = gameform.save(commit=False)
            gameobj.user = request.user
            gameobj.cup_id = cup_id
            gameobj.save()
            game_id = gameobj.game_id
            game_name = gameobj.game_name

            team_role = 'hometeam'
            for team_name in team_names:
                if Team.objects.filter(user_id=request.user.id,team_name=team_name).exists():
                    teamvalue = Team.objects.filter(user_id=request.user.id,team_name=team_name).last()
                    team_id=teamvalue.team_id
                    if Team_Cup.objects.filter(cup_id=cup_id,team_id=team_id).exists():
                        saveTG(team_id,game_id,team_role)
                    else:
                        team_cup = Team_Cup(cup_id=cup_id,team_id=team_id)
                        team_cup.save()
                        saveTG(team_id,game_id,team_role)
                else:
                    teamform = TeamForm()
                    teamobj = teamform.save(commit=False)
                    teamobj.team_name = team_name
                    teamobj.user = request.user
                    teamobj.save()
                    team_id = teamobj.team_id
                    team_cup = Team_Cup(cup_id=cup_id,team_id=team_id)
                    team_cup.save()
                    saveTG(team_id,game_id,team_role)

                team_role = 'awayteam'

            messages.success(request, f'您已成功新增「{game_name}」的比賽記錄')
            return redirect('game', cup_id=cup_id)
    else:
        teamform = TeamForm()
        gameform = GameForm()
    context = {
        'teamform': teamform,
        'gameform': gameform,
        'cupvalue': cupvalue,
        'gamevalues': gamevalues,
        'hometeam_gamevalues': hometeam_gamevalues,
        'awayteam_gamevalues': awayteam_gamevalues,
    }
    return render(request, 'dashboard/game.html', context)

@login_required
def game_delete(request, cup_id, game_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    gamevalue = Game.objects.get(game_id=game_id)
    game_name = gamevalue.game_name
    if request.method == 'POST':
        gamevalue.delete()
        messages.success(request, f'您已成功刪除「{game_name}」的比賽記錄')
        return redirect('game', cup_id=cup_id)
    context = {
        'cupvalue': cupvalue,
    }
    return render(request, 'dashboard/game_delete.html', context)

@login_required
def game_update(request, cup_id, game_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    gamevalue = Game.objects.get(game_id=game_id)
    game_name1 = gamevalue.game_name
    if request.method == 'POST':
        gameform = GameForm(request.POST, instance=gamevalue)
        if gameform.is_valid():
            gameform.save()
            game_name2 = gamevalue.game_name
            messages.success(request, f'您已成功將「{game_name1}」的比賽名稱修改為「{game_name2}」')
            return redirect('game', cup_id=cup_id)
    else:
        gameform = GameForm(instance=gamevalue)
    context = {
        'cupvalue': cupvalue,
        'gameform': gameform,
    }
    return render(request, 'dashboard/game_update.html', context)


@login_required
def batter(request, team_id):
    # team_playervalues = Team_Player.objects.filter(team_id=team_id)
    # battingvalues = Batting.objects.filter(team_id=3)
    # for team_playervalue in team_playervalues:
    #     battingvalues = Batting.objects.filter(player_id=team_playervalue.player_id, team_id=team_id)
    #     for battingvalue in battingvalues:
    #         print(battingvalue.player.player_name)
    context = {
    }
    return render(request, 'dashboard/batter.html', context)

@login_required
def pitcher(request):
    return render(request, 'dashboard/pitcher.html')


@login_required
def manager(request):
    managers = User.objects.all()
    managers_count = managers.count()
    context = {
        'managers': managers,
        'managers_count': managers_count,
    }
    return render(request, 'dashboard/manager.html', context)


@login_required
def manager_detail(request, pk):
    managers = User.objects.get(id=pk)
    context = {
        'managers': managers
    }
    return render(request, 'dashboard/manager_detail.html', context)

def battingSaveTP(team_id,player_id):
    team_playerform = Team_PlayerForm()
    team_playerobj = team_playerform.save(commit=False)
    team_playerobj.team_id = team_id
    team_playerobj.player_id = player_id
    team_playerobj.save()

def battingSaveGP(battingform,game_id,team_id,player_id,player_order,player_role):
    battingobj = battingform.save(commit=False)
    battingobj.game_id = game_id
    battingobj.team_id = team_id
    battingobj.player_id = player_id
    battingobj.player_order = player_order
    battingobj.player_role = player_role
    battingobj.save()

@login_required
def batting(request, cup_id, game_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="hometeam")
    hometeamvalue = team_gamevalue.team
    gamevalue = team_gamevalue.game
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="awayteam")
    awayteamvalue = team_gamevalue.team
    hometeam_playervalues = Team_Player.objects.filter(team_id=hometeamvalue.team_id)
    awayteam_playervalues = Team_Player.objects.filter(team_id=awayteamvalue.team_id)
    hometeam_battingvalues = Batting.objects.filter(game_id=game_id,team_id=hometeamvalue.team_id).order_by('player_order')
    awayteam_battingvalues = Batting.objects.filter(game_id=game_id,team_id=awayteamvalue.team_id).order_by('player_order')

    if request.method == 'POST':
        playerform = PlayerForm(request.POST)
        battingform = BattingForm(request.POST)
        player_id = request.POST.get('player_id')
        team_id = request.POST.get('team_id')
        player_order = request.POST.get('player_order')
        player_role = request.POST.get('player_role')
        if playerform.is_valid() and battingform.is_valid():
            player_name = playerform.cleaned_data.get('player_name')
            if player_id != "":
                try:
                    battingvalue = Batting.objects.get(game_id=game_id,player_id=player_id)
                    messages.success(request, f'您先前已建立過「{battingvalue.player.player_name}」的本場成績')
                    return redirect('batting', cup_id=cup_id, game_id=game_id)
                except:
                    try:
                        team_playervalue = Team_Player.objects.get(team_id=team_id,player_id=player_id)
                        battingSaveGP(battingform,game_id,team_id,player_id,player_order,player_role)
                        messages.success(request, f'您已成功新增「{team_playervalue.player.player_name}」的本場成績')
                        return redirect('batting', cup_id=cup_id, game_id=game_id)
                    except:
                        battingSaveTP(team_id,player_id)
                        battingSaveGP(battingform,game_id,team_id,player_id,player_order,player_role)
                        team_playervalue = Team_Player.objects.get(team_id=team_id,player_id=player_id)
                        messages.success(request, f'您已成功新增「{team_playervalue.player.player_name}」的本場成績')
                        return redirect('batting', cup_id=cup_id, game_id=game_id)
            elif player_id == "":
                playerobj = playerform.save(commit=False)
                playerobj.save()
                player_id = playerobj.player_id
                battingSaveTP(team_id,player_id)
                battingSaveGP(battingform,game_id,team_id,player_id,player_order,player_role)
                messages.success(request, f'您已成功建立「{player_name}」的本場成績')
                return redirect('batting', cup_id=cup_id, game_id=game_id)
        else:
            messages.warning(request, f'請您確實完成選單！')
            return redirect('batting', cup_id=cup_id, game_id=game_id)
    else:
        playerform = PlayerForm()
        battingform = BattingForm()
    context = {
        'playerform': playerform,
        'battingform': battingform,
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeamvalue,
        'awayteamvalue': awayteamvalue,
        'hometeam_playervalues': hometeam_playervalues,
        'awayteam_playervalues': awayteam_playervalues,
        'hometeam_battingvalues': hometeam_battingvalues,
        'awayteam_battingvalues': awayteam_battingvalues,
    }
    return render(request, 'dashboard/batting.html', context)

@login_required
def batting_delete(request, cup_id, game_id, player_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    battingvalue = Batting.objects.get(game_id=game_id, player_id=player_id)
    if request.method == 'POST':
        battingvalue.delete()
        return redirect('batting', cup_id=cup_id, game_id=game_id)
    context = {
        'cupvalue': cupvalue,
        'battingvalue': battingvalue,
    }
    return render(request, 'dashboard/batting_delete.html', context)

@login_required
def batting_update(request, cup_id, game_id, player_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    battingvalue = Batting.objects.get(game_id=game_id, player_id=player_id)
    playervalue = Player.objects.get(player_id=player_id)
    if request.method == 'POST':
        playerform = PlayerForm(request.POST, instance=playervalue)
        battingform = BattingForm(request.POST, instance=battingvalue)
        if playerform.is_valid() and battingform.is_valid():
            playerform.save()
            battingform.save()
            player_name = playervalue.player_name
            messages.success(request, f'您已成功修改「{player_name}」的本場成績')
            return redirect('batting', cup_id=cup_id, game_id=game_id)
    else:
        playerform = PlayerForm(instance=playervalue)
        battingform = BattingForm(instance=battingvalue)
    context = {
        'cupvalue': cupvalue,
        'playerform': playerform,
        'battingform': battingform,
        'battingvalue': battingvalue,
    }
    return render(request, 'dashboard/batting_update.html', context)

@login_required
def batting_data(request, cup_id, game_id, player_id):
    cupvalue = Cup.objects.get(cup_id=cup_id)
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="hometeam")
    hometeamvalue = team_gamevalue.team
    gamevalue = team_gamevalue.game
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="awayteam")
    awayteamvalue = team_gamevalue.team
    battingvalue = Batting.objects.get(game_id=game_id, player_id=player_id)
    value = Batting.objects.get(game_id=game_id, player_id=player_id)
    try:
        ab = value.b_pa-(value.b_bb+value.b_hbp+value.b_sf+value.b_sh)
    except:
        ab = 0
    try:
        h = value.b_single+value.b_double+value.b_triple+value.b_hr
    except:
        h = 0

    try:
        avg = round(h/ab,3)
    except:
        avg = 0
    try:
        obp = round((h+value.b_bb+value.b_hbp)/(ab+value.b_bb+value.b_hbp+value.b_sf),3)
    except:
        obp = 0
    try:
        slg = round(((1*value.b_single)+(2*value.b_double)+(3*value.b_triple)+(4*value.b_hr))/ab,3)
    except:
        slg = 0
    try:
        ops = round(obp+slg,3)
    except:
        ops = 0
    try:
        iso = round(slg-avg,3)
    except:
        iso = 0
    try:
        babip = round((h-value.b_hr)/(ab-value.b_so-value.b_hr+value.b_sf),3)
    except:
        babip = 0
    try:
        bip = round((ab-value.b_so-value.b_hr+value.b_sf)/(ab+value.b_bb+value.b_hbp+value.b_sf)*100,1)
    except:
        bip = 0
    try:
        bbp = round((value.b_bb-value.b_ibb)/value.b_pa*100,1)
    except:
        bbp = 0
    try:
        sobb = round(value.b_so/(value.b_bb-value.b_ibb),3)
    except:
        sobb = 0
    try:
        sop = round(value.b_so/value.b_pa*100,1)
    except:
        sop = 0

    avg = ('%.3f'%avg)
    obp = ('%.3f'%obp)
    slg = ('%.3f'%slg)
    ops = ('%.3f'%ops)
    iso = ('%.3f'%iso)
    babip = ('%.3f'%babip)
    bip = ('%.1f'%bip)
    bbp = ('%.1f'%bbp)
    sobb = ('%.3f'%sobb)
    sop = ('%.1f'%sop)
    context = {
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeamvalue,
        'awayteamvalue': awayteamvalue,
        'battingvalue': battingvalue,
        'avg': avg,
        'obp': obp,
        'slg': slg,
        'ops': ops,
        'iso': iso,
        'babip': babip,
        'bip': bip,
        'bbp': bbp,
        'sobb': sobb,
        'sop': sop,
    }
    return render(request, 'dashboard/batting_data.html', context)


@login_required
def pitching(request, game_id):
    # gamevalue = Game.objects.get(game_id=game_id)
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="hometeam")
    hometeamvalue = team_gamevalue.team
    gamevalue = team_gamevalue.game
    team_gamevalue = Team_Game.objects.get(game_id=game_id, team_role="awayteam")
    awayteamvalue = team_gamevalue.team
    playervalues = Player.objects.filter(user_id=request.user.id)
    hometeam_pitchingvalues = Pitching.objects.filter(game_id=game_id,team_id=hometeamvalue.team_id)
    awayteam_pitchingvalues = Pitching.objects.filter(game_id=game_id,team_id=awayteamvalue.team_id)

    if request.method == 'POST':
        playerform = PlayerForm(request.POST)
        pitchingform = PitchingForm(request.POST)
        player_id = request.POST.get('player_id')
        team_id = request.POST.get('team_id')
        player_role = request.POST.get('player_role')
        if team_id != "請選擇所屬球隊" and player_role != "請選擇守備位置" and playerform.is_valid() and pitchingform.is_valid():
            player_name = playerform.cleaned_data.get('player_name')
            if player_id != "選擇先前曾建立過的球員":
                try:
                    pitchingvalue = Pitching.objects.get(game_id=game_id,player_id=player_id)
                    messages.success(request, f'您先前已建立過「{pitchingvalue.player.player_name}」的本場成績')
                    return redirect('pitching', game_id=game_id)
                except:
                    try:
                        team_playervalue = Team_Player.objects.get(team_id=team_id,player_id=player_id)

                        pitchingobj = pitchingform.save(commit=False)
                        pitchingobj.game_id = game_id
                        pitchingobj.team_id = team_id
                        pitchingobj.player_id = player_id
                        pitchingobj.player_role = player_role
                        pitchingobj.save()
                        messages.success(request, f'您已成功新增「{team_playervalue.player.player_name}」的本場成績')
                        return redirect('pitching', game_id=game_id)
                    except:
                        team_playerform = Team_PlayerForm()
                        team_playerobj = team_playerform.save(commit=False)
                        team_playerobj.team_id = team_id
                        team_playerobj.player_id = player_id
                        team_playerobj.save()

                        pitchingobj = pitchingform.save(commit=False)
                        pitchingobj.game_id = game_id
                        pitchingobj.team_id = team_id
                        pitchingobj.player_id = player_id
                        pitchingobj.player_role = player_role
                        pitchingobj.save()
                        team_playervalue = Team_Player.objects.get(team_id=team_id,player_id=player_id)
                        messages.success(request, f'您已成功新增「{team_playervalue.player.player_name}」的本場成績')
                        return redirect('pitching', game_id=game_id)
            elif player_id == "選擇先前曾建立過的球員":
                if player_name == "":
                    messages.success(request, f'請確實完成選單！')
                    return redirect('pitching', game_id=game_id)
                playerobj = playerform.save(commit=False)
                playerobj.save()
                player_id = playerobj.player_id
                
                team_playerform = Team_PlayerForm()
                team_playerobj = team_playerform.save(commit=False)
                team_playerobj.team_id = team_id
                team_playerobj.player_id = player_id
                team_playerobj.save()

                pitchingobj = pitchingform.save(commit=False)
                pitchingobj.game_id = game_id
                pitchingobj.team_id = team_id
                pitchingobj.player_id = player_id
                pitchingobj.player_role = player_role
                pitchingobj.save()
                messages.success(request, f'您已成功建立「{player_name}」的本場成績')
                return redirect('pitching', game_id=game_id)
        else:
            messages.warning(request, f'請您確實完成選單！')
            return redirect('pitching', game_id=game_id)
    else:
        playerform = PlayerForm()
        pitchingform = PitchingForm()
    context = {
        'playerform': playerform,
        'pitchingform': pitchingform,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeamvalue,
        'awayteamvalue': awayteamvalue,
        'playervalues': playervalues,
        'hometeam_pitchingvalues': hometeam_pitchingvalues,
        'awayteam_pitchingvalues': awayteam_pitchingvalues,
    }
    return render(request, 'dashboard/pitching.html', context)

@login_required
def pitching_data(request, game_id, player_id):
    pitchingvalue = Pitching.objects.get(game_id=game_id, player_id=player_id)
    value = Pitching.objects.get(game_id=game_id, player_id=player_id)
    try:
        h = value.p_single+value.p_double+value.p_triple+value.p_hr
    except:
        h = 0

    try:
        era = round((value.p_er*9/value.p_ip),3)
    except:
        era = 0
    try:
        whip = round((h+value.p_bb)/value.p_ip,3)
    except:
        whip = 0
    try:
        h9 = round((h*9/value.p_ip),3)
    except:
        h9 = 0
    try:
        hr9 = round((value.p_hr*9/value.p_ip),3)
    except:
        hr9 = 0
    try:
        bb9 = round((value.p_bb*9/value.p_ip),3)
    except:
        bb9 = 0
    try:
        so9 = round((value.p_so*9/value.p_ip),3)
    except:
        so9 = 0

    era = ('%.3f'%era)
    whip = ('%.3f'%whip)
    h9 = ('%.3f'%h9)
    hr9 = ('%.3f'%hr9)
    bb9 = ('%.3f'%bb9)
    so9 = ('%.3f'%so9)
    context = {
        'pitchingvalue': pitchingvalue,
        'era': era,
        'whip': whip,
        'h9': h9,
        'hr9': hr9,
        'bb9': bb9,
        'so9': so9,
    }
    return render(request, 'dashboard/pitching_data.html', context)
