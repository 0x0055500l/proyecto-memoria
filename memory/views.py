from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg # <-- Importa Avg
from .models import Player, MemoryGame
import os
import json
import time
#esta la usamos para manejar fechas y horas de honduras
from django.utils.timezone import localtime
# --- NUEVOS FORMULARIOS para validar form ---
from .forms import CustomRegisterForm, CustomLoginForm
# este es usado para el geoip
import requests
from ipware.ip import get_client_ip
#este es usado para el rate limit de login y hacer lock
from axes.handlers.proxy import AxesProxyHandler

#vista de 404
def handler_404_view(request, exception):
    # Redirige a la página de login
    return redirect('login')

# --- Vistas de Autenticación (Reutilizadas) ---
def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Player.objects.create(user=user) # Crea el perfil de jugador
	    #logica vieja antes de fallo de doble auth
            #login(request, user)

            # --- ESPECIFICAMOS EL BACKEND ---
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # ----------------------------------------
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # --- VERIFICA SI EL USUARIO ESTÁ BLOQUEADO ANTES DE HACER NADA ---
    # Obtenemos el "manejador" de axes para este request
    if AxesProxyHandler.is_locked(request):
        return render(request, 'login.html', {
            'form': CustomLoginForm(),
            'is_locked_out': True
        })
    # --------------------------------------------------

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    # --- PASA EL 'is_locked_out' COMO False POR DEFECTO ---
    return render(request, 'login.html', {'form': form, 'is_locked_out': False})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- Vistas del Perfil y Menú (Adaptadas) ---
@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def profile_view(request):
    #player = request.user.player

    # Si el perfil existe, lo trae. Si no existe (usuario viejo), lo crea.
    player, created = Player.objects.get_or_create(user=request.user)

    # Buscamos el historial del juego de memoria
    game_history = MemoryGame.objects.filter(player=player).order_by('-date_played')

    # Calcular Tiempo Promedio
    avg_data = game_history.aggregate(avg_time=Avg('time_spent'))
    avg_time = avg_data.get('avg_time', 0)

    # Calcular Ranking Global
    all_players = Player.objects.order_by('-best_score', '-total_victories')
    rank = 0
    for i, p in enumerate(all_players):
        if p.user == request.user:
            rank = i + 1
            break

    # --- PREPARAR DATOS PARA EL GRÁFICO ---
    # Tomamos las últimas 10 partidas (están ordenadas por fecha descendente)
    last_10_games = game_history[:10]
    
    # Las invertimos para que el gráfico vaya de izquierda (antiguo) a derecha (nuevo)
    games_for_chart = reversed(list(last_10_games))
    
    labels = [] # Fechas
    data_time = [] # Tiempos
    
    
    for game in games_for_chart:
        # Formateamos la fecha: por ejemplo "14 Nov 15:30"
        local_date = localtime(game.date_played)
        labels.append(local_date.strftime("%d %b %H:%M"))
        data_time.append(game.time_spent)

    # ---------------------------------------------

    context = {
        'player': player,
        'game_history': game_history,
        'avg_time': avg_time, # Nueva stat
        'rank': rank, # Nueva stat
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data_time),
    }
    return render(request, 'profile.html', context)

# --- Vistas del Juego de Memoria (Nuevas) ---
@login_required
def memory_game_view(request, difficulty):
    # 1. Obtener la semilla de la URL o generar una nueva
    seed = request.GET.get('seed')
    
    if not seed:
        # Generamos una semilla basada en el tiempo actual si no viene una
        seed = str(int(time.time()))

    context = {
        'difficulty': difficulty,
        'seed': seed  # <--- Pasamos la semilla al HTML
    }
    return render(request, 'memory_game.html', context)

@login_required
def save_game_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            #player = request.user.player           usado anteriormente pero cambiado por nueva implementacion mas robusta
            player, created = Player.objects.get_or_create(user=request.user)

            # --- Logica de pais de jugador ---
            if not player.country:
                client_ip, is_routable = get_client_ip(request)
                
                # Solo buscamos IPs públicas, no locales (como 127.0.0.1 o 192.168...)
                if client_ip and is_routable:
                    try:
                        # Preguntamos a la API por el país
                        api_url = f"http://ip-api.com/json/{client_ip}?fields=status,country,message"
                        response = requests.get(api_url, timeout=3) # 3 segundos de espera
                        
                        if response.status_code == 200:
                            api_data = response.json()
                            if api_data.get('status') == 'success':
                                player.country = api_data.get('country', 'Desconocido')
                            else:
                                # Pasa si la API no reconoce la IP
                                player.country = "N/A"
                        else:
                            player.country = "Error API"

                    except Exception as e:
                        print(f"Error API GeoIP: {e}")
                        player.country = "Error Red"
                else:
                    player.country = "Local" # Para que no vuelva a preguntar
            # ---------------------------------------------------

            # --- Lógica de Puntaje ---
            score = 0
            time = data['time_spent']
            fails = data['fails']
            difficulty_mult = 1 # Básico
            
            if data['difficulty'] == 'medio':
                difficulty_mult = 1.5
            elif data['difficulty'] == 'avanzado':
                difficulty_mult = 2.5
            
            if data['is_win']:
                # Premio por ganar
                score = (10000 / (time + 1)) * difficulty_mult
                score -= (fails * 20) # Penalización por fallos
            else:
                # Puntaje de consolación (basado en pares)
                score = (data.get('pairs_found', 0) * 10) * difficulty_mult
            
            score = max(0, int(score)) # Asegura que no sea negativo
            # -------------------------

            MemoryGame.objects.create(
                player=player,
                difficulty=data['difficulty'][0].upper(),
                time_spent=time,
                moves=data['moves'],
                fails=fails,
                is_win=data['is_win'],
                score=score  # <-- Guarda el puntaje
            )

            player.games_played += 1
            if data['is_win']:
                player.total_victories += 1
            else:
                player.total_defeats += 1
            
            # Actualiza el mejor puntaje
            if score > player.best_score:
                player.best_score = score
                
            player.save()

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'bad_request'}, status=400)
@login_required
def ranking_view(request):
    # Obtiene el Top 25, ordenado por mejor puntaje, y luego por más victorias
    players_list = Player.objects.order_by('-best_score', '-total_victories')[:25]
    
    context = {
        'players_list': players_list,
    }
    return render(request, 'ranking.html', context)
