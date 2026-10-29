from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum

from .models import Cup, Player, Game, Team, Team_Cup, Team_Game, Team_Player, Batting, Pitching
from .forms import CupForm, PlayerForm, GameForm, TeamForm, BattingForm, PitchingForm


def calculate_batting_stats(b_pa, b_single, b_double, b_triple, b_hr, b_bb, b_ibb, b_hbp, b_so, b_sh, b_sf):
    """計算打擊進階數據，避免除以零異常"""
    ab = b_pa - (b_bb + b_hbp + b_sf + b_sh)
    h = b_single + b_double + b_triple + b_hr
    tb = b_single + (2 * b_double) + (3 * b_triple) + (4 * b_hr)

    avg = (h / ab) if ab > 0 else 0.0

    obp_denom = ab + b_bb + b_hbp + b_sf
    obp = ((h + b_bb + b_hbp) / obp_denom) if obp_denom > 0 else 0.0

    slg = (tb / ab) if ab > 0 else 0.0
    ops = obp + slg
    iso = slg - avg

    babip_denom = ab - b_so - b_hr + b_sf
    babip = ((h - b_hr) / babip_denom) if babip_denom > 0 else 0.0

    bip = (babip_denom / obp_denom * 100) if obp_denom > 0 else 0.0

    unintentional_bb = max(b_bb - b_ibb, 0)
    bbp = (unintentional_bb / b_pa * 100) if b_pa > 0 else 0.0
    sobb = (b_so / unintentional_bb) if unintentional_bb > 0 else 0.0
    sop = (b_so / b_pa * 100) if b_pa > 0 else 0.0

    return {
        'pa': b_pa,
        'ab': ab,
        'h': h,
        'avg': f'{avg:.3f}',
        'obp': f'{obp:.3f}',
        'slg': f'{slg:.3f}',
        'ops': f'{ops:.3f}',
        'iso': f'{iso:.3f}',
        'babip': f'{babip:.3f}',
        'bip': f'{bip:.1f}',
        'bbp': f'{bbp:.1f}',
        'sobb': f'{sobb:.3f}',
        'sop': f'{sop:.1f}',
    }


def calculate_pitching_stats(p_ip, p_single, p_double, p_triple, p_hr, p_bb, p_so, p_er):
    """計算投球進階數據，避免除以零異常"""
    h = p_single + p_double + p_triple + p_hr

    if p_ip > 0:
        era = (p_er * 9.0) / p_ip
        whip = (h + p_bb) / float(p_ip)
        h9 = (h * 9.0) / p_ip
        hr9 = (p_hr * 9.0) / p_ip
        bb9 = (p_bb * 9.0) / p_ip
        so9 = (p_so * 9.0) / p_ip
    else:
        era = whip = h9 = hr9 = bb9 = so9 = 0.0

    return {
        'ip': p_ip,
        'er': p_er,
        'h': h,
        'bb': p_bb,
        'so': p_so,
        'era': f'{era:.3f}',
        'whip': f'{whip:.3f}',
        'h9': f'{h9:.3f}',
        'hr9': f'{hr9:.3f}',
        'bb9': f'{bb9:.3f}',
        'so9': f'{so9:.3f}',
    }


# ==============================
# 首頁與球隊管理視圖
# ==============================

@login_required
def index(request):
    return render(request, 'dashboard/index.html')


@login_required
def team(request):
    return render(request, 'dashboard/team.html')


@login_required
def hometeam(request):
    teamvalues = Team.objects.filter(user=request.user, team_game__team_role="hometeam").distinct()
    context = {
        'teamvalues': teamvalues,
    }
    return render(request, 'dashboard/hometeam.html', context)


@login_required
def awayteam(request):
    teamvalues = Team.objects.filter(user=request.user, team_game__team_role="awayteam").distinct()
    context = {
        'teamvalues': teamvalues,
    }
    return render(request, 'dashboard/awayteam.html', context)


@login_required
def hometeam_delete(request, team_id):
    teamvalue = get_object_or_404(Team, team_id=team_id, user=request.user)
    team_name = teamvalue.team_name
    if request.method == 'POST':
        teamvalue.delete()
        messages.success(request, f'您已成功刪除「{team_name}」球隊資料')
        return redirect('hometeam')
    return render(request, 'dashboard/hometeam_delete.html', {'hometeamvalue': teamvalue})


@login_required
def hometeam_update(request, team_id):
    teamvalue = get_object_or_404(Team, team_id=team_id, user=request.user)
    team_name1 = teamvalue.team_name
    if request.method == 'POST':
        hometeamform = TeamForm(request.POST, instance=teamvalue)
        if hometeamform.is_valid():
            hometeamform.save()
            team_name2 = teamvalue.team_name
            messages.success(request, f'您已成功將「{team_name1}」的球隊名稱修改為「{team_name2}」')
            return redirect('hometeam')
    else:
        hometeamform = TeamForm(instance=teamvalue)
    context = {
        'hometeamform': hometeamform,
        'teamvalue': teamvalue,
    }
    return render(request, 'dashboard/hometeam_update.html', context)


# ==============================
# 盃賽 (Cup) 管理視圖
# ==============================

@login_required
def cup(request):
    cupvalues = Cup.objects.filter(user=request.user).order_by('-cup_id')

    if request.method == 'POST':
        cupform = CupForm(request.POST)
        if cupform.is_valid():
            cupobj = cupform.save(commit=False)
            cupobj.user = request.user
            cupobj.save()
            messages.success(request, f'您已成功新增「{cupobj.cup_name}」的盃賽記錄')
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
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    cup_name = cupvalue.cup_name
    if request.method == 'POST':
        cupvalue.delete()
        messages.success(request, f'您已成功刪除「{cup_name}」的盃賽記錄')
        return redirect('cup')
    return render(request, 'dashboard/cup_delete.html', {'cupvalue': cupvalue})


@login_required
def cup_update(request, cup_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
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
        'cupvalue': cupvalue,
    }
    return render(request, 'dashboard/cup_update.html', context)


# ==============================
# 比賽 (Game) 管理視圖
# ==============================

@login_required
def game(request, cup_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalues = Game.objects.filter(cup=cupvalue).order_by('-game_id')
    hometeam_gamevalues = Team_Game.objects.filter(game__cup=cupvalue, team_role="hometeam")
    awayteam_gamevalues = Team_Game.objects.filter(game__cup=cupvalue, team_role="awayteam")

    if request.method == 'POST':
        gameform = GameForm(request.POST)
        hometeam_name = (request.POST.get('hometeam') or '').strip()
        awayteam_name = (request.POST.get('awayteam') or '').strip()

        if gameform.is_valid() and hometeam_name and awayteam_name:
            gameobj = gameform.save(commit=False)
            gameobj.cup = cupvalue
            gameobj.save()

            for team_role, team_name in (('hometeam', hometeam_name), ('awayteam', awayteam_name)):
                team_obj, _ = Team.objects.get_or_create(user=request.user, team_name=team_name)
                Team_Cup.objects.get_or_create(cup=cupvalue, team=team_obj)
                Team_Game.objects.get_or_create(game=gameobj, team=team_obj, team_role=team_role)

            messages.success(request, f'您已成功新增「{gameobj.game_name}」的比賽記錄')
            return redirect('game', cup_id=cup_id)
        else:
            messages.warning(request, '請確認比賽名稱與兩隊隊名皆已填寫！')
    else:
        gameform = GameForm()

    context = {
        'gameform': gameform,
        'cupvalue': cupvalue,
        'gamevalues': gamevalues,
        'hometeam_gamevalues': hometeam_gamevalues,
        'awayteam_gamevalues': awayteam_gamevalues,
    }
    return render(request, 'dashboard/game.html', context)


@login_required
def game_delete(request, cup_id, game_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    game_name = gamevalue.game_name
    if request.method == 'POST':
        gamevalue.delete()
        messages.success(request, f'您已成功刪除「{game_name}」的比賽記錄')
        return redirect('game', cup_id=cup_id)
    context = {
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
    }
    return render(request, 'dashboard/game_delete.html', context)


@login_required
def game_update(request, cup_id, game_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
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
        'gamevalue': gamevalue,
        'gameform': gameform,
    }
    return render(request, 'dashboard/game_update.html', context)


# ==============================
# 球隊選手累計數據 (打者 / 投手)
# ==============================

@login_required
def batter(request, team_id):
    teamvalue = get_object_or_404(Team, team_id=team_id, user=request.user)
    players = Player.objects.filter(batting__team=teamvalue).distinct()
    players_stats = []

    for player in players:
        totals = Batting.objects.filter(team=teamvalue, player=player).aggregate(
            pa=Sum('b_pa'), single=Sum('b_single'), double=Sum('b_double'),
            triple=Sum('b_triple'), hr=Sum('b_hr'), bb=Sum('b_bb'),
            ibb=Sum('b_ibb'), hbp=Sum('b_hbp'), so=Sum('b_so'),
            sh=Sum('b_sh'), sf=Sum('b_sf')
        )
        stats = calculate_batting_stats(
            totals['pa'] or 0, totals['single'] or 0, totals['double'] or 0,
            totals['triple'] or 0, totals['hr'] or 0, totals['bb'] or 0,
            totals['ibb'] or 0, totals['hbp'] or 0, totals['so'] or 0,
            totals['sh'] or 0, totals['sf'] or 0
        )
        stats['name'] = player.player_name
        players_stats.append(stats)

    context = {
        'teamvalue': teamvalue,
        'players_stats': players_stats,
    }
    return render(request, 'dashboard/batter.html', context)


@login_required
def pitcher(request, team_id=None):
    if team_id is None:
        return redirect('team')

    teamvalue = get_object_or_404(Team, team_id=team_id, user=request.user)
    players = Player.objects.filter(pitching__team=teamvalue).distinct()
    pitchers_stats = []

    for player in players:
        totals = Pitching.objects.filter(team=teamvalue, player=player).aggregate(
            ip=Sum('p_ip'), single=Sum('p_single'), double=Sum('p_double'),
            triple=Sum('p_triple'), hr=Sum('p_hr'), bb=Sum('p_bb'),
            so=Sum('p_so'), er=Sum('p_er')
        )
        stats = calculate_pitching_stats(
            totals['ip'] or 0, totals['single'] or 0, totals['double'] or 0,
            totals['triple'] or 0, totals['hr'] or 0, totals['bb'] or 0,
            totals['so'] or 0, totals['er'] or 0
        )
        stats['name'] = player.player_name
        pitchers_stats.append(stats)

    context = {
        'teamvalue': teamvalue,
        'pitchers_stats': pitchers_stats,
    }
    return render(request, 'dashboard/pitcher.html', context)


# ==============================
# 經理人管理視圖 (Admin / Staff)
# ==============================

@login_required
def manager(request):
    managers = User.objects.all()
    context = {
        'managers': managers,
        'managers_count': managers.count(),
    }
    return render(request, 'dashboard/manager.html', context)


@login_required
def manager_detail(request, pk):
    manager_obj = get_object_or_404(User, id=pk)
    return render(request, 'dashboard/manager_detail.html', {'managers': manager_obj})


# ==============================
# 單場打擊成績 (Batting)
# ==============================

@login_required
def batting(request, cup_id, game_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)

    hometeam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="hometeam")
    awayteam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="awayteam")
    hometeamvalue = hometeam_gamevalue.team
    awayteamvalue = awayteam_gamevalue.team

    hometeam_playervalues = Team_Player.objects.filter(team=hometeamvalue)
    awayteam_playervalues = Team_Player.objects.filter(team=awayteamvalue)
    hometeam_battingvalues = Batting.objects.filter(game=gamevalue, team=hometeamvalue).order_by('player_order')
    awayteam_battingvalues = Batting.objects.filter(game=gamevalue, team=awayteamvalue).order_by('player_order')

    if request.method == 'POST':
        playerform = PlayerForm(request.POST)
        battingform = BattingForm(request.POST)
        player_id = (request.POST.get('player_id') or '').strip()
        team_id = (request.POST.get('team_id') or '').strip()
        player_order = request.POST.get('player_order')
        player_role = request.POST.get('player_role')

        if playerform.is_valid() and battingform.is_valid() and team_id:
            team_obj = get_object_or_404(Team, team_id=team_id)

            if player_id:
                player_obj = get_object_or_404(Player, player_id=player_id)
                if Batting.objects.filter(game=gamevalue, player=player_obj).exists():
                    messages.warning(request, f'您先前已建立過「{player_obj.player_name}」的本場成績')
                    return redirect('batting', cup_id=cup_id, game_id=game_id)
            else:
                player_name = playerform.cleaned_data.get('player_name')
                player_obj = Player.objects.create(player_name=player_name)

            Team_Player.objects.get_or_create(team=team_obj, player=player_obj)

            battingobj = battingform.save(commit=False)
            battingobj.game = gamevalue
            battingobj.team = team_obj
            battingobj.player = player_obj
            battingobj.player_order = player_order
            battingobj.player_role = player_role
            battingobj.save()

            messages.success(request, f'您已成功新增「{player_obj.player_name}」的本場成績')
            return redirect('batting', cup_id=cup_id, game_id=game_id)
        else:
            messages.warning(request, '請您確實完成選單與各項欄位填寫！')
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
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    battingvalue = get_object_or_404(Batting, game=gamevalue, player_id=player_id)
    player_name = battingvalue.player.player_name

    if request.method == 'POST':
        battingvalue.delete()
        messages.success(request, f'您已成功刪除「{player_name}」的打擊成績')
        return redirect('batting', cup_id=cup_id, game_id=game_id)

    context = {
        'cupvalue': cupvalue,
        'battingvalue': battingvalue,
    }
    return render(request, 'dashboard/batting_delete.html', context)


@login_required
def batting_update(request, cup_id, game_id, player_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    battingvalue = get_object_or_404(Batting, game=gamevalue, player_id=player_id)
    playervalue = battingvalue.player

    if request.method == 'POST':
        playerform = PlayerForm(request.POST, instance=playervalue)
        battingform = BattingForm(request.POST, instance=battingvalue)
        if playerform.is_valid() and battingform.is_valid():
            playerform.save()
            battingform.save()
            messages.success(request, f'您已成功修改「{playervalue.player_name}」的本場成績')
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
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    hometeam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="hometeam")
    awayteam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="awayteam")
    battingvalue = get_object_or_404(Batting, game=gamevalue, player_id=player_id)

    stats = calculate_batting_stats(
        battingvalue.b_pa, battingvalue.b_single, battingvalue.b_double,
        battingvalue.b_triple, battingvalue.b_hr, battingvalue.b_bb,
        battingvalue.b_ibb, battingvalue.b_hbp, battingvalue.b_so,
        battingvalue.b_sh, battingvalue.b_sf
    )

    context = {
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeam_gamevalue.team,
        'awayteamvalue': awayteam_gamevalue.team,
        'battingvalue': battingvalue,
        **stats,
    }
    return render(request, 'dashboard/batting_data.html', context)


# ==============================
# 單場投球成績 (Pitching)
# ==============================

@login_required
def pitching(request, cup_id, game_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)

    hometeam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="hometeam")
    awayteam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="awayteam")
    hometeamvalue = hometeam_gamevalue.team
    awayteamvalue = awayteam_gamevalue.team

    # 取得兩隊所有選手（排除使用者關聯錯誤）
    playervalues = Player.objects.filter(team_player__team__in=[hometeamvalue, awayteamvalue]).distinct()
    hometeam_pitchingvalues = Pitching.objects.filter(game=gamevalue, team=hometeamvalue)
    awayteam_pitchingvalues = Pitching.objects.filter(game=gamevalue, team=awayteamvalue)

    if request.method == 'POST':
        playerform = PlayerForm(request.POST)
        pitchingform = PitchingForm(request.POST)
        player_id = (request.POST.get('player_id') or '').strip()
        team_id = (request.POST.get('team_id') or '').strip()
        player_role = (request.POST.get('player_role') or '').strip()

        if team_id not in ('', '請選擇所屬球隊') and player_role not in ('', '請選擇守備位置') and pitchingform.is_valid():
            team_obj = get_object_or_404(Team, team_id=team_id)

            if player_id and player_id != '選擇先前曾建立過的球員':
                player_obj = get_object_or_404(Player, player_id=player_id)
                if Pitching.objects.filter(game=gamevalue, player=player_obj).exists():
                    messages.warning(request, f'您先前已建立過「{player_obj.player_name}」的本場成績')
                    return redirect('pitching', cup_id=cup_id, game_id=game_id)
            else:
                if not playerform.is_valid():
                    messages.warning(request, '請輸入球員姓名！')
                    return redirect('pitching', cup_id=cup_id, game_id=game_id)
                player_name = playerform.cleaned_data.get('player_name')
                player_obj = Player.objects.create(player_name=player_name)

            Team_Player.objects.get_or_create(team=team_obj, player=player_obj)

            pitchingobj = pitchingform.save(commit=False)
            pitchingobj.game = gamevalue
            pitchingobj.team = team_obj
            pitchingobj.player = player_obj
            pitchingobj.player_role = player_role
            pitchingobj.save()

            messages.success(request, f'您已成功新增「{player_obj.player_name}」的本場成績')
            return redirect('pitching', cup_id=cup_id, game_id=game_id)
        else:
            messages.warning(request, '請您確實完成選單！')
            return redirect('pitching', cup_id=cup_id, game_id=game_id)
    else:
        playerform = PlayerForm()
        pitchingform = PitchingForm()

    context = {
        'playerform': playerform,
        'pitchingform': pitchingform,
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeamvalue,
        'awayteamvalue': awayteamvalue,
        'playervalues': playervalues,
        'hometeam_pitchingvalues': hometeam_pitchingvalues,
        'awayteam_pitchingvalues': awayteam_pitchingvalues,
    }
    return render(request, 'dashboard/pitching.html', context)


@login_required
def pitching_delete(request, cup_id, game_id, player_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    pitchingvalue = get_object_or_404(Pitching, game=gamevalue, player_id=player_id)
    player_name = pitchingvalue.player.player_name

    if request.method == 'POST':
        pitchingvalue.delete()
        messages.success(request, f'您已成功刪除「{player_name}」的投球成績')
        return redirect('pitching', cup_id=cup_id, game_id=game_id)

    context = {
        'cupvalue': cupvalue,
        'pitchingvalue': pitchingvalue,
    }
    return render(request, 'dashboard/pitching_delete.html', context)


@login_required
def pitching_update(request, cup_id, game_id, player_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    pitchingvalue = get_object_or_404(Pitching, game=gamevalue, player_id=player_id)
    playervalue = pitchingvalue.player

    if request.method == 'POST':
        playerform = PlayerForm(request.POST, instance=playervalue)
        pitchingform = PitchingForm(request.POST, instance=pitchingvalue)
        if playerform.is_valid() and pitchingform.is_valid():
            playerform.save()
            pitchingform.save()
            messages.success(request, f'您已成功修改「{playervalue.player_name}」的投球成績')
            return redirect('pitching', cup_id=cup_id, game_id=game_id)
    else:
        playerform = PlayerForm(instance=playervalue)
        pitchingform = PitchingForm(instance=pitchingvalue)

    context = {
        'cupvalue': cupvalue,
        'playerform': playerform,
        'pitchingform': pitchingform,
        'pitchingvalue': pitchingvalue,
        'playervalue': playervalue,
    }
    return render(request, 'dashboard/pitching_update.html', context)


@login_required
def pitching_data(request, cup_id, game_id, player_id):
    cupvalue = get_object_or_404(Cup, cup_id=cup_id, user=request.user)
    gamevalue = get_object_or_404(Game, game_id=game_id, cup=cupvalue)
    hometeam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="hometeam")
    awayteam_gamevalue = get_object_or_404(Team_Game, game=gamevalue, team_role="awayteam")
    pitchingvalue = get_object_or_404(Pitching, game=gamevalue, player_id=player_id)

    stats = calculate_pitching_stats(
        pitchingvalue.p_ip, pitchingvalue.p_single, pitchingvalue.p_double,
        pitchingvalue.p_triple, pitchingvalue.p_hr, pitchingvalue.p_bb,
        pitchingvalue.p_so, pitchingvalue.p_er
    )

    context = {
        'cupvalue': cupvalue,
        'gamevalue': gamevalue,
        'hometeamvalue': hometeam_gamevalue.team,
        'awayteamvalue': awayteam_gamevalue.team,
        'pitchingvalue': pitchingvalue,
        **stats,
    }
    return render(request, 'dashboard/pitching_data.html', context)
