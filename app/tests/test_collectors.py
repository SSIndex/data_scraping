import sys
import os
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

import asyncio
import logging
from datetime import datetime
import pandas as pd
from config.test_settings import API_KEYS, TEST_CONFIG, OUTPUT_DIRS
from collectors.places_collector import PlacesCollector
from collectors.youtube_collector import YouTubeCollector
from collectors.twitter_collector import TwitterCollector
from collectors.news_collector import NewsCollector
from collectors.facebook_collector import FacebookCollector

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_collector(collector_name, collector_instance):
    """Prueba un collector específico"""
    logger.info(f"\n{'='*50}\nProbando {collector_name}")
    
    try:
        # Datos de prueba
        test_company = {
            'name': TEST_CONFIG['company_name'],
            'country': TEST_CONFIG['country']
        }
        
        # Ejecutar collector
        result = await collector_instance.collect_data([test_company])
        
        # Verificar resultados
        if result:
            # Intentar leer el archivo más reciente del directorio correspondiente
            directory = OUTPUT_DIRS[collector_name.lower()]
            files = os.listdir(directory)
            if files:
                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(directory, x)))
                df = pd.read_csv(os.path.join(directory, latest_file))
                logger.info(f"Resultados encontrados: {len(df)} registros")
                # Mostrar primeros registros
                logger.info("\nPrimeros registros:")
                print(df.head())
            else:
                logger.warning("No se encontraron archivos de resultados")
        else:
            logger.error("La recolección no fue exitosa")
            
    except Exception as e:
        logger.error(f"Error probando {collector_name}: {str(e)}")
        return False
    
    return True

async def run_tests():
    """Ejecuta pruebas para todos los collectors"""
    collectors = {
        'Places': PlacesCollector(),
        'YouTube': YouTubeCollector(),
        'Twitter': TwitterCollector(),
        'News': NewsCollector(),
        'Facebook': FacebookCollector()
    }
    
    results = {}
    
    for name, collector in collectors.items():
        results[name] = await test_collector(name, collector)
        # Esperar un poco entre pruebas para evitar límites de rata
        await asyncio.sleep(2)
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("RESUMEN DE PRUEBAS")
    print("="*50)
    for name, success in results.items():
        status = "✅ ÉXITO" if success else "❌ FALLÓ"
        print(f"{name}: {status}")

if __name__ == "__main__":
    # Verificar API keys
    print("\nVerificando API keys configuradas:")
    for api_name, api_key in API_KEYS.items():
        status = "✅ Configurada" if api_key else "❌ No configurada"
        print(f"{api_name}: {status}")
    
    # Ejecutar pruebas
    print("\nIniciando pruebas...")
    asyncio.run(run_tests())