import logging
import asyncio
from typing import List, Dict
import redis
from datetime import datetime
import traceback

from collectors.places_collector import PlacesCollector
from collectors.facebook_collector import FacebookCollector
from collectors.youtube_collector import YouTubeCollector
from collectors.twitter_collector import TwitterCollector
from collectors.news_collector import NewsCollector
from config.settings import EXECUTION_INTERVALS, REDIS_CONFIG

logger = logging.getLogger(__name__)

class DataCollectorOrchestrator:
    def __init__(self):
        self.collectors = {
            'places': PlacesCollector(),
            'facebook': FacebookCollector(),
            'youtube': YouTubeCollector(),
            'twitter': TwitterCollector(),
            'news': NewsCollector()
        }
        self.redis_client = redis.Redis(**REDIS_CONFIG)
        
    def get_active_companies(self) -> List[Dict]:
        """Obtiene la lista de empresas activas desde Redis"""
        try:
            companies = []
            for key in self.redis_client.scan_iter("company:*"):
                company_data = self.redis_client.hgetall(key)
                if company_data.get(b'active', b'true').decode() == 'true':
                    companies.append({
                        'name': company_data[b'name'].decode(),
                        'country': company_data[b'country'].decode()
                    })
            return companies
        except Exception as e:
            logger.error(f"Error obteniendo empresas activas: {str(e)}")
            return []

    def update_last_run(self, collector_name: str):
        """Actualiza la marca de tiempo de última ejecución"""
        try:
            self.redis_client.hset(
                'collector_last_runs',
                collector_name,
                datetime.now().timestamp()
            )
        except Exception as e:
            logger.error(f"Error actualizando última ejecución para {collector_name}: {str(e)}")

    def should_run_collector(self, collector_name: str) -> bool:
        """Determina si un collector debe ejecutarse basado en su intervalo"""
        try:
            last_run = self.redis_client.hget('collector_last_runs', collector_name)
            if not last_run:
                return True
                
            last_run_time = datetime.fromtimestamp(float(last_run))
            interval_hours = EXECUTION_INTERVALS.get(collector_name, 24)
            next_run = last_run_time + timedelta(hours=interval_hours)
            
            return datetime.now() >= next_run
        except Exception as e:
            logger.error(f"Error verificando tiempo de ejecución para {collector_name}: {str(e)}")
            return True

    async def run_collector(self, collector_name: str, companies: List[Dict]):
        """Ejecuta un collector específico"""
        try:
            if not self.should_run_collector(collector_name):
                logger.info(f"Saltando {collector_name}, aún no es tiempo de ejecutar")
                return
                
            logger.info(f"Iniciando recolección de datos para {collector_name}")
            collector = self.collectors[collector_name]
            success = await collector.collect_data(companies)
            
            if success:
                self.update_last_run(collector_name)
                logger.info(f"Recolección exitosa para {collector_name}")
            else:
                logger.error(f"Falló la recolección para {collector_name}")
                
        except Exception as e:
            logger.error(f"Error ejecutando {collector_name}: {str(e)}")
            logger.error(traceback.format_exc())

    async def run_all_collectors(self):
        """Ejecuta todos los collectors"""
        try:
            companies = self.get_active_companies()
            if not companies:
                logger.warning("No hay empresas activas para procesar")
                return

            tasks = []
            for collector_name in self.collectors:
                task = asyncio.create_task(
                    self.run_collector(collector_name, companies)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error en la ejecución principal: {str(e)}")
            logger.error(traceback.format_exc())

    async def start(self):
        """Inicia el proceso de recolección"""
        while True:
            try:
                await self.run_all_collectors()
                # Esperar 5 minutos antes de la siguiente verificación
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error en el ciclo principal: {str(e)}")
                await asyncio.sleep(60)  # Esperar 1 minuto en caso de error

if __name__ == "__main__":
    orchestrator = DataCollectorOrchestrator()
    asyncio.run(orchestrator.start())