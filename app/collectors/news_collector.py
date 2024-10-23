import logging
import pandas as pd
import requests
from typing import List, Dict, Optional
import time
from datetime import datetime, timedelta
from config.settings import API_KEYS, OUTPUT_DIRS, SEARCH_CONFIG

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.api_key = API_KEYS['news']
        self.output_dir = OUTPUT_DIRS['news']
        self.days_back = SEARCH_CONFIG['news_days_back']
        
    def verify_api_key(self) -> bool:
        """Verifica que la API key sea válida"""
        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': 'test',
                'apiKey': self.api_key,
                'pageSize': 1
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando API key: {str(e)}")
            return False

    def search_news(self, company_name: str) -> List[Dict]:
        """Busca noticias para una empresa"""
        try:
            url = 'https://newsapi.org/v2/everything'
            
            # Calcular rango de fechas
            to_date = datetime.now()
            from_date = to_date - timedelta(days=self.days_back)
            
            params = {
                'q': f'"{company_name}"',
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'relevancy',
                'apiKey': self.api_key,
                'pageSize': 100  # Máximo permitido por la API
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            
            news_data = []
            for article in articles:
                article_data = {
                    'company_name': company_name,
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'source_name': article.get('source', {}).get('name'),
                    'author': article.get('author'),
                    'published_at': article.get('publishedAt'),
                    'content': article.get('content')
                }
                news_data.append(article_data)
            
            return news_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la solicitud para {company_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado buscando noticias para {company_name}: {str(e)}")
            return []

    def collect_and_save(self, companies: List[Dict]) -> bool:
        """Recolecta y guarda datos para una lista de empresas"""
        try:
            all_data = []
            
            for company in companies:
                logger.info(f"Procesando empresa: {company['name']}")
                news = self.search_news(company['name'])
                all_data.extend(news)
                time.sleep(1)  # Esperar entre solicitudes
            
            if all_data:
                df = pd.DataFrame(all_data)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{self.output_dir}/news_data_{timestamp}.csv"
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
    collector = NewsCollector()
    test_companies = [
        {"name": "Tesla", "country": "United States"},
        {"name": "Netflix", "country": "United States"}
    ]
    import asyncio
    asyncio.run(collector.collect_data(test_companies))