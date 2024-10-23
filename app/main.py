import uvicorn
from core.api import app
from core.orchestrator import DataCollectorOrchestrator
import asyncio
import threading

def run_orchestrator():
    """Ejecuta el orchestrator en un thread separado"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    orchestrator = DataCollectorOrchestrator()
    loop.run_until_complete(orchestrator.start())

if __name__ == "__main__":
    # Iniciar el orchestrator en un thread separado
    orchestrator_thread = threading.Thread(target=run_orchestrator, daemon=True)
    orchestrator_thread.start()
    
    # Iniciar la API
    uvicorn.run(app, host="0.0.0.0", port=8000)