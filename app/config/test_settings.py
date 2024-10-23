import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# API Keys (usar las mismas que en settings.py)
API_KEYS = {
    'google_places': os.getenv('api_key_google_3'),
    'youtube': os.getenv('YOUTUBE_API_KEY'),
    'twitter_bearer': os.getenv('bearer_token'),
    'news': os.getenv('NEWS_API_KEY'),
    'outscrapper': os.getenv('OUTSCRAPPER')
}

# Configuración específica para pruebas
TEST_CONFIG = {
    'company_name': 'Tesla',
    'country': 'United States',
    'days_back': 2,
    'max_results': 10
}

# Directorios base para pruebas
BASE_DIR = Path(__file__).parent.parent
TEST_DATA_DIR = BASE_DIR / 'test_data'

# Configuraciones de salida para pruebas
OUTPUT_DIRS = {
    'places': str(TEST_DATA_DIR / 'places'),
    'facebook': str(TEST_DATA_DIR / 'facebook'),
    'youtube': str(TEST_DATA_DIR / 'youtube'),
    'twitter': str(TEST_DATA_DIR / 'twitter'),
    'news': str(TEST_DATA_DIR / 'news')
}

# Crear directorios de prueba si no existen
for directory in OUTPUT_DIRS.values():
    os.makedirs(directory, exist_ok=True)