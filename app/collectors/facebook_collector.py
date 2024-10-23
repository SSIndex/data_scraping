import logging
import pandas as pd
import requests
from typing import List, Dict, Optional
import time
from config.settings import API_KEYS, OUTPUT_DIRS

logger = logging.getLogger(__name__)

class FacebookCollector:
    def __init__(self):
        self.api_key = API_KEYS['outscrapper']  # Usando Outscrapper para Facebook
        self.output_dir = OUTPUT_DIRS['facebook']
        
    def verify_api_key(self) -> bool:
        """Verifica que la API key sea válida"""
        try:
            url = "https://api.app.outscraper.com/facebook/reviews"
            headers = {"X-API-KEY": self.api_key}
            params = {'query': 'test', 'async': 'false'}
            response = requests.get(url, headers=headers, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando API key: {str(e)}")
            return False

    def get_facebook_reviews(self, company_name: str) -> List[Dict]:
        """Obtiene reseñas de Facebook para una empresa"""
        try:
            url = "https://api.app.outscraper.com/facebook/reviews"
            headers = {"X-API-KEY": self.api_key}
            params = {
                'query': company_name,
                'async': 'false'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            reviews_data = response.json().get('data', [])
            if not reviews_data:
                logger.warning(f"No se encontraron reseñas para {company_name}")
                return []
                
            # Procesar primera lista de resultados
            reviews = reviews_data[0] if reviews_data else []
            
            processed_reviews = []
            for review in reviews:
                review_data = {
                    'company_name': company_name,
                    'reviewer_name': review.get('reviewer_name'),
                    'rating': review.get('rating'),
                    'review_text': review.get('review_text'),
                    'review_time': review.get('review_time'),
                    'review_likes': review.get('review_likes'),
                    'reviewer_profile': review.get('reviewer_profile')
                }
                processed_reviews.append(review_data)
                
            return processed_reviews
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la solicitud para {company_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado obteniendo reseñas para {company_name}: {str(e)}")
            return []

    def collect_and_save(self, companies: List[Dict]) -> bool:
        """Recolecta y guarda datos para una lista de empresas"""
        try:
            all_data = []
            
            for company in companies:
                logger.info(f"Procesando empresa: {company['name']}")
                reviews = self.get_facebook_reviews(company['name'])
                all_data.extend(reviews)
                time.sleep(2)  # Esperar entre solicitudes
            
            if all_data:
                df = pd.DataFrame(all_data)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{self.output_dir}/facebook_data_{timestamp}.csv"
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
    collector = FacebookCollector()
    test_companies = [
        {"name": "Tesla", "country": "United States"},
        {"name": "Netflix", "country": "United States"}
    ]
    import asyncio
    asyncio.run(collector.collect_data(test_companies))