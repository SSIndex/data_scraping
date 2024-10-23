import logging
import pandas as pd
import requests
from typing import List, Dict, Optional
import time
from config.settings import API_KEYS, OUTPUT_DIRS, SEARCH_CONFIG

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        self.api_key = API_KEYS['youtube']
        self.output_dir = OUTPUT_DIRS['youtube']
        self.max_results = SEARCH_CONFIG['youtube_max_results']
        
    def verify_api_key(self) -> bool:
        """Verifica que la API key sea válida"""
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': 'test',
                'type': 'video',
                'key': self.api_key,
                'maxResults': 1
            }
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando API key: {str(e)}")
            return False

    def search_videos(self, company_name: str, keywords: List[str]) -> List[Dict]:
        """Busca videos relacionados con una empresa"""
        all_videos = []
        
        for keyword in keywords:
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': f"{company_name} {keyword}",
                    'type': 'video',
                    'maxResults': self.max_results,
                    'key': self.api_key
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                items = response.json().get('items', [])
                
                for item in items:
                    video_data = {
                        'company_name': company_name,
                        'search_keyword': keyword,
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    all_videos.append(video_data)
                
                time.sleep(1)  # Esperar entre solicitudes
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la solicitud para {company_name} con keyword {keyword}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error inesperado buscando videos para {company_name}: {str(e)}")
                continue
                
        return all_videos

    def collect_and_save(self, companies: List[Dict]) -> bool:
        """Recolecta y guarda datos para una lista de empresas"""
        try:
            all_data = []
            keywords = ['review', 'opinion', 'experience', 'tutorial', 'news']
            
            for company in companies:
                logger.info(f"Procesando empresa: {company['name']}")
                videos = self.search_videos(company['name'], keywords)
                all_data.extend(videos)
            
            if all_data:
                df = pd.DataFrame(all_data)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{self.output_dir}/youtube_data_{timestamp}.csv"
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
    collector = YouTubeCollector()
    test_companies = [
        {"name": "Tesla", "country": "United States"},
        {"name": "Netflix", "country": "United States"}
    ]
    import asyncio
    asyncio.run(collector.collect_data(test_companies))