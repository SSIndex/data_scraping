import logging
import pandas as pd
import requests
from typing import List, Dict, Optional
import time
from config.settings import API_KEYS, OUTPUT_DIRS

logger = logging.getLogger(__name__)

class PlacesCollector:
    def __init__(self):
        self.api_key = API_KEYS['google_places']
        self.output_dir = OUTPUT_DIRS['places']
        
    def verify_api_key(self) -> bool:
        """Verifica que la API key sea válida"""
        try:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': 'test',
                'key': self.api_key
            }
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando API key: {str(e)}")
            return False

    def search_places(self, company_name: str, country: str) -> List[Dict]:
        """Busca lugares para una empresa"""
        try:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f"{company_name} in {country}",
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            results = response.json().get('results', [])
            
            places_data = []
            for place in results:
                place_data = {
                    'company_name': company_name,
                    'place_id': place.get('place_id'),
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                    'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('user_ratings_total')
                }
                places_data.append(place_data)
            
            return places_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la solicitud para {company_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado buscando lugares para {company_name}: {str(e)}")
            return []

    def collect_and_save(self, companies: List[Dict]) -> bool:
        """Recolecta y guarda datos para una lista de empresas"""
        try:
            all_data = []
            
            for company in companies:
                logger.info(f"Procesando empresa: {company['name']}")
                places = self.search_places(company['name'], company['country'])
                all_data.extend(places)
                # Esperar entre solicitudes para evitar límites de rata
                time.sleep(1)
            
            if all_data:
                df = pd.DataFrame(all_data)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{self.output_dir}/places_data_{timestamp}.csv"
                df.to_csv(filename, index=False)
                logger.info(f"Datos guardados en {filename}")
                return True
            
            logger.warning("No se encontraron datos para guardar")
            return False
            
        except Exception as e:
            logger.error(f"Error guardando datos: {str(e)}")
            return False
            
    async def collect_data(self, companies: List[Dict]) -> bool:
        """Punto de entrada principal para la recolección de datos"""
        if not self.verify_api_key():
            logger.error("API key inválida")
            return False
            
        return self.collect_and_save(companies)

if __name__ == "__main__":
    # Ejemplo de uso
    collector = PlacesCollector()
    test_companies = [
        {"name": "Tesla", "country": "United States"},
        {"name": "Netflix", "country": "United States"}
    ]
    import asyncio
    asyncio.run(collector.collect_data(test_companies))