import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# API Keys
API_KEYS = {
    'google_places': os.getenv('api_key_google_3'),
    'youtube': os.getenv('YOUTUBE_API_KEY'),
    'twitter_bearer': os.getenv('bearer_token'),
    'news': os.getenv('NEWS_API_KEY'),
    'outscrapper': os.getenv('OUTSCRAPPER')
}

# Intervalos de ejecución en horas
EXECUTION_INTERVALS = {
    'places': 24,
    'facebook': 12,
    'youtube': 48,
    'twitter': 0.5,
    'news': 6
}

# Directorios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuraciones de salida
OUTPUT_DIRS = {
    'places': os.path.join(BASE_DIR, 'data', 'places'),
    'facebook': os.path.join(BASE_DIR, 'data', 'facebook'),
    'youtube': os.path.join(BASE_DIR, 'data', 'youtube'),
    'twitter': os.path.join(BASE_DIR, 'data', 'twitter'),
    'news': os.path.join(BASE_DIR, 'data', 'news')
}

# Configuración para búsquedas
SEARCH_CONFIG = {
    'youtube_max_results': 50,
    'twitter_max_results': 100,
    'news_days_back': 30,
    'youtube_languages': ['en', 'es'],
    'news_languages': ['en', 'es']
}

# Crear directorios de salida si no existen
for directory in OUTPUT_DIRS.values():
    os.makedirs(directory, exist_ok=True)