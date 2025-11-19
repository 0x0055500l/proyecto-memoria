from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Player, MemoryGame
import json
from .forms import CustomRegisterForm, CustomLoginForm
import requests
from ipware.ip import get_client_ip
from django.conf import settings
from django.db.models import Avg
import os
import time
from django.utils.timezone import localtime

# --- IMPORTACIÓN DE SEGURIDAD (AXES) ---
from axes.handlers.proxy import AxesProxyHandler

# --- IMPORTACIÓN PARA SESIÓN ---
from django.contrib.sessions.models import Session

# --- VISTA DE ERROR 404 ---
def handler_404_view(request, exception):
    return redirect('login')

# --- VISTA DE ESTADO DE SESIÓN (PING) ---
def session_status_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'status': 'active'})
    else:
        return JsonResponse({'status': 'inactive'}, status=401)

# --- VISTAS DE AUTENTICACIÓN ---
def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Player.objects.create(user=user)
            # Usamos el backend estándar para el autologin tras registro
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # 1. Verificar bloqueo por intentos fallidos (Axes)
    if AxesProxyHandler.is_locked(request):
        return render(request, 'login.html', {
            'form': CustomLoginForm(), 
            'is_locked_out': True
        })

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # 2. Autenticar pasando el request (necesario para Axes)
            user = authenticate(request=request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # 3. Lógica de SESIÓN ÚNICA (Actualizar llave en BD)
                try:
                    # Usamos get_or_create por seguridad
                    player, created = Player.objects.get_or_create(user=user)
                    
                    # Guardamos la llave de la sesión actual en el perfil
                    if request.session.session_key:
                        player.last_session_key = request.session.session_key
                        player.save()
                        
                except Exception as e:
                    print(f"Error actualizando sesión única: {e}")
                
                return redirect('home')
    else:
        form = CustomLoginForm()
        
    return render(request, 'login.html', {'form': form, 'is_locked_out': False})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- VISTAS PRINCIPALES ---
@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def profile_view(request):
    player, created = Player.objects.get_or_create(user=request.user)
    game_history = MemoryGame.objects.filter(player=player).order_by('-date_played')
    
    avg_data = game_history.aggregate(avg_time=Avg('time_spent'))
    avg_time = avg_data.get('avg_time', 0)
    
    all_players = Player.objects.order_by('-best_score', '-total_victories')
    rank = 0
    for i, p in enumerate(all_players):
        if p.user == request.user:
            rank = i + 1
            break
            
    # Datos para el Gráfico
    last_10_games = game_history[:10]
    games_for_chart = reversed(list(last_10_games))
    labels = []
    data_time = []
    
    for game in games_for_chart:
        local_date = localtime(game.date_played)
        labels.append(local_date.strftime("%d %b %H:%M"))
        data_time.append(game.time_spent)

    context = {
        'player': player,
        'game_history': game_history,
        'avg_time': avg_time, 
        'rank': rank,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data_time),
    }
    return render(request, 'profile.html', context)

@login_required
def ranking_view(request):
    players_list = Player.objects.order_by('-best_score', '-total_victories')[:25]
    context = {'players_list': players_list}
    return render(request, 'ranking.html', context)

@login_required
def memory_game_view(request, difficulty):
    seed = request.GET.get('seed')
    if not seed:
        seed = str(int(time.time()))

    context = {
        'difficulty': difficulty,
        'seed': seed
    }
    return render(request, 'memory_game.html', context)

@login_required
def save_game_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player, created = Player.objects.get_or_create(user=request.user)

            # Lógica de País (GeoIP)
            if not player.country:
                client_ip, is_routable = get_client_ip(request)
                if client_ip and is_routable:
                    try:
                        api_url = f"http://ip-api.com/json/{client_ip}?fields=status,country"
                        response = requests.get(api_url, timeout=3)
                        if response.status_code == 200:
                            api_data = response.json()
                            if api_data.get('status') == 'success':
                                player.country = api_data.get('country', 'Desconocido')
                            else:
                                player.country = "N/A"
                        else:
                            player.country = "Error API"
                    except Exception:
                        player.country = "Error Red"
                else:
                    player.country = "Local"

            # Lógica de Puntuación
            score = 0
            time_val = data.get('time_spent', 0)
            fails = data.get('fails', 0)
            difficulty_mult = 1
            
            if data.get('difficulty') == 'medio':
                difficulty_mult = 1.5
            elif data.get('difficulty') == 'avanzado':
                difficulty_mult = 2.5 # O 5.0 si hiciste el cambio para el profe
            
            if data.get('is_win'):
                score = (10000 / (time_val + 1)) * difficulty_mult
                score -= (fails * 20)
            else:
                score = (data.get('pairs_found', 0) * 10) * difficulty_mult
            
            score = max(0, int(score))

            MemoryGame.objects.create(
                player=player,
                difficulty=data['difficulty'][0].upper(),
                time_spent=time_val,
                moves=data['moves'],
                fails=fails,
                is_win=data['is_win'],
                score=score
            )

            player.games_played += 1
            if data['is_win']:
                player.total_victories += 1
            else:
                player.total_defeats += 1
            
            if score > player.best_score:
                player.best_score = score
                
            player.save()

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'bad_request'}, status=400)
