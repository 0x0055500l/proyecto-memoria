from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.sessions.models import Session

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo verificamos si el usuario está autenticado y no es una solicitud de logout
        if request.user.is_authenticated and request.path != reverse('logout'):
            try:
                player = request.user.player
                
                # Verificamos si la sesión en BD no coincide con la actual
                if player.last_session_key and player.last_session_key != request.session.session_key:
                    
                    # 1. Cerramos la sesión local
                    logout(request)
                    
                    # 2. Preparamos la URL de login con el mensaje de error
                    login_url = reverse('login') + '?error=duplicate_session'
                    
                    # 3. Redirigimos
                    return redirect(login_url)
                
                # Si es una sesión nueva o no tiene clave, la actualizamos
                if not player.last_session_key:
                    player.last_session_key = request.session.session_key
                    player.save()
                    
            except Exception:
                # Si pasa algo raro (usuario sin perfil, etc), no bloqueamos
                pass

        response = self.get_response(request)
        return response
