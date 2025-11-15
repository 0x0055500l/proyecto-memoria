<div align="center">

# 🧠 Memory Game - Proyecto de Arquitectura de Computadoras

![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)

<p align="center">
  <strong>Una implementación moderna y contenerizada del clásico juego de memoria, desarrollada para la clase de Organización y Arquitectura de Computadoras en UTH Honduras.</strong>
</p>

[Ver Demo](#) • [Reportar Bug](https://github.com/0x0055500l/proyecto-memoria/issues)

</div>

---

## 📋 Tabla de Contenidos
1. [Sobre el Proyecto](#-sobre-el-proyecto)
2. [Características Principales](#-características-principales)
3. [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
4. [Instalación y Despliegue](#-instalación-y-despliegue)
5. [Guía de Uso](#-guía-de-uso)
6. [Equipo de Desarrollo](#-equipo-de-desarrollo)

---

## 🚀 Sobre el Proyecto

Este proyecto tiene como objetivo diseñar e implementar el juego **Memory Game** utilizando el framework Django y contenedores Docker. El enfoque principal es la aplicación de principios fundamentales de arquitectura de computadoras, gestión eficiente de recursos y aislamiento de entornos.

El sistema permite a los usuarios registrarse, competir en diferentes niveles de dificultad, guardar sus estadísticas en tiempo real y competir en un ranking global con detección de país de origen.

---

## ✨ Características Principales

### 🎮 Experiencia de Juego
* **3 Niveles de Dificultad:**
    * 🟢 **Básico:** 12 Cartas (6 pares) - Ideal para novatos (15 intentos).
    * 🟡 **Medio:** 16 Cartas (8 pares) - Un reto equilibrado (20 intentos).
    * 🔴 **Avanzado:** 20 Cartas (10 pares) - Solo para expertos (25 intentos).
* **Feedback Interactivo:** Sonidos de victoria, derrota y volteo de cartas (con opción de *Mute*).
* **Mecánicas:** Contador de movimientos, fallos, temporizador y botón de reinicio en tiempo real.
* **Efectos Visuales:** Animaciones CSS, logos animados y Modo Oscuro automático/manual.

### 👤 Perfil y Estadísticas
* **Historial Completo:** Registro de todas las partidas jugadas con fecha, resultado (victoria/derrota) y puntaje.
* **Estadísticas Avanzadas:** Cálculo de tiempo promedio, tasa de victorias/derrotas y mejor puntaje personal.
* **Ranking Global:** Tabla de posiciones (Top 25) que compara a todos los jugadores por puntaje.

### 🌍 Geolocalización Inteligente
* Detección automática del país del jugador (vía API de `ip-api.com`) al guardar la partida.
* *(Nota: En entornos locales de desarrollo 192.168.x.x mostrará "Local")*.

### 🛡️ Seguridad y Rendimiento
* Recuperación de Cuenta: Flujo completo de "Olvidé mi contraseña" implementado con SMTP de
 Gmail.
* Límite de Intentos (Rate Limiting): Protección contra ataques de fuerza bruta. Bloquea al
 usuario/IP tras 3 intentos fallidos (django-axes).
* Protección contra ataques CSRF en todas las peticiones POST y AJAX.
* Manejo eficiente de archivos estáticos en producción (`DEBUG=False`) usando **WhiteNoise**.
* Páginas de error 404 personalizadas para evitar fugas de información.

---

## 🛠 Arquitectura y Tecnologías

El proyecto utiliza una arquitectura basada en microservicios orquestados por Docker:

* **Backend:** Python + Django 5.
* **Base de Datos:** PostgreSQL 14 (Persistencia mediante Volúmenes Docker).
* **Frontend:** HTML5, CSS3 (con animaciones), JavaScript (Vanilla), Bootstrap 5.3.
* **Contenerización:** Docker y Docker Compose para aislar el entorno y facilitar la portabilidad.
* **Librerías Clave:** `requests` (API GeoIP), `whitenoise` (Static files), `psycopg2` (DB connector), `django-ipware` (Detección de IP), `django-axes` (Rate Limiting).

---

## 📦 Instalación y Despliegue

Sigue estos pasos para ejecutar el proyecto en la maquina local.

### Prerrequisitos
* Docker Desktop instalado y corriendo.
* Git instalado.

### Paso 1: Clonar el Repositorio
```bash
git clone [https://github.com/0x0055500l/proyecto-memoria.git](https://github.com/0x0055500l/proyecto-memoria.git)
cd proyecto-memoria
```

### Paso 2: Crear el Archivo de Entorno ( .env )
-  Este es el paso de seguridad más importante.
```bash
 nano .env
```
- Pega el siguiente contenido, reemplazando con tus propios valores:
```bash
# Secreto de Django (puedes generar uno nuevo online)
DJANGO_SECRET_KEY=tu-django-secret-key-aqui
# Poner en False para producción
DJANGO_DEBUG=False

# Database configuration
DB_HOST=db
DB_PORT=5432
DB_USER=admin
DB_PASS=admin123
DB_NAME=memorygamedb

# POSTGRES DATABASE
POSTGRES_DB=memorygamedb
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# Credenciales de Gmail para reseteo de contraseña
# EMail CONFIG
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-app-16-letras
```

### Paso 3: Construir y Levantar Contenedores
Este comando descargará las imágenes necesarias, instalará las dependencias (Python/pip) y creará los contenedores.

```bash
docker-compose up -d --build
```
Notas:
- `(Espera a que termine de construir y levantar los servicios web y db).`

### Paso 4: Aplicar Migraciones (Crucial)
Este paso configura la base de datos PostgreSQL inicial y aplica todos los modelos (Player, MemoryGame, etc.).

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Paso 5: (Opcional) Crear un Superusuario
Para acceder al panel de admin en `/admin/ `.
```bash
docker-compose exec web python manage.py createsuperuser
```

### Paso 6: Acceder
¡Listo! Abre tu navegador y visita:

```bash
http://localhost:8000
```
 (O la IP de el VM/VPS)

## 📖 Guía de Uso
- `Registro/Login:` Crea una cuenta nueva. El sistema validará que tu correo y usuario sean únicos.
- `Límite de Intentos:` Si fallas el login 3 veces, el sistema te bloqueará por 1 minuto.
- `Recuperar Contraseña:` Si olvidas tu clave, usa el enlace en el login. Recibirás un correo de Gmail
 con instrucciones.
- `Inicio:` Selecciona una dificultad. Cada tarjeta te indica el número de intentos permitidos.
- `Juego:`
  - Encuentra los pares antes de que se acabe el tiempo o tus intentos.
  - Usa el botón 🔄 para reiniciar la partida si te atascas.
  - Usa el botón 🔊 para silenciar el juego.
- `Perfil:` Al terminar una partida, serás redirigido a tu perfil. Revisa tu progreso, tu rango global y tu historial detallado.
- `Ranking:` Compara tu "Mejor Puntaje" y tu país con el Top 25 global.

## 👥 Equipo de Desarrollo
Proyecto desarrollado por estudiantes de Ingeniería en Computación de UTH Honduras.

| Número de Cuenta | Integrante | Rol |
| :--- | :--- | :--- |
| **201810020200** | **Josseth Alejandro Bautista Fuentes** | **Lead Developer** |
| 202010010006 | Jonathan Galeb Regalado Rivera | Developer |
| 200711120001 | Oscar Hernández | Developer |
| 202010010089 | Yisela Diney Molina Sosa | UI Designer |
| 202110010161 | Bayron Rolando García Paz | Developer |
| 202310110180 | Kensy Valeska Garcia Paz | UI Designer |
| 202110010339 | Eduardo Alfredo Estrada Valenzuela | Developer |

<div align="center"> <p>Desarrollado con ❤️ y mucho café ☕</p> <p>Universidad Tecnológica de Honduras (UTH)</p> </div>
