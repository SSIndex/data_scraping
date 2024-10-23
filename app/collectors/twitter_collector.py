import logging
import pandas as pd
import tweepy
from typing import List, Dict, Optional
import time
from config.settings import API_KEYS, OUTPUT_DIRS, SEARCH_CONFIG

logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        self.bearer_token = API_KEYS['twitter_bearer']
        self.output_dir = OUTPUT_DIRS['twitter']
        self.max_results = SEARCH_CONFIG['twitter_max_results']
        self.client = self._init_client()
        
    def _init_client(self) -> Optional[tweepy.Client]:
        """Inicializa el cliente de Twitter"""
        try:
            return tweepy.Client(bearer_token=self.bearer_token)
        except Exception as e:
            logger.error(f"Error inicializando cliente de Twitter: {str(e)}")
            return None

    def verify_credentials(self) -> bool:
        """Verifica que las credenciales sean válidas"""
        try:
            # Intenta una búsqueda simple para verificar credenciales
            self.client.search_recent_tweets(query="test", max_results=10)
            return True
        except Exception as e:
            logger.error(f"Error verificando credenciales: {str(e)}")
            return False

    def search_tweets(self, company_name: str) -> List[Dict]:
        """Busca tweets relacionados con una empresa"""
        try:
            # Construir query con exclusión de retweets
            query = f'"{company_name}" -is:retweet'
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=self.max_results,
                tweet_fields=['created_at', 'lang', 'public_metrics']
            )
            
            if not tweets.data:
                logger.warning(f"No se encontraron tweets para {company_name}")
                return []
            
            tweets_data = []
            for tweet in tweets.data:
                tweet_data = {
                    'company_name': company_name,
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'language': tweet.lang,
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'quote_count': tweet.public_metrics['quote_count']
                }
                tweets_data.append(tweet_data)
            
            return tweets_data
            
        except Exception as e:
            logger.error(f"Error buscando tweets para {company_name}: {str(e)}")
            return []

    def collect_and_save(self, companies: List[Dict]) -> bool:
        """Recolecta y guarda datos para una lista de empresas"""
        try:
            all_data = []
            
            for company in companies:
                logger.info(f"Procesando empresa: {company['name']}")
                tweets = self.search_tweets(company['name'])
                all_data.extend(tweets)
                time.sleep(2)  # Esperar entre solicitudes
            
            if all_data:
                df = pd.DataFrame(all_data)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{self.output_dir}/twitter_data_{timestamp}.csv"
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
        if not self.client:
            logger.error("Cliente de Twitter no inicializado")
            return False
            
        if not self.verify_credentials():
            logger.error("Credenciales de Twitter inválidas")
            return False
            
        return self.collect_and_save(companies)

if __name__ == "__main__":
    # Ejemplo de uso
    collector = TwitterCollector()
    test_companies = [
        {"name": "Tesla", "country": "United States"},
        {"name": "Netflix", "country": "United States"}
    ]
    import asyncio
    asyncio.run(collector.collect_data(test_companies))