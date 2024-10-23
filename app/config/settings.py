import logging
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import uvicorn
from typing import List, Dict
import redis
from pydantic import BaseModel

# Importar configuraciones
from config.settings import (
    API_KEYS, 
    EXECUTION_INTERVALS, 
    OUTPUT_DIRS, 
    REDIS_CONFIG, 
    LOG_CONFIG
)

# Configurar logging
logging.basicConfig(**LOG_CONFIG)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(title="Data Collector API")

# Inicializar Redis
redis_client = redis.Redis(**REDIS_CONFIG)

# Modelo para empresas
class Company(BaseModel):
    name: str
    country: str
    active: bool = True

# Scheduler
scheduler = BackgroundScheduler()

# Endpoints
@app.post("/companies/")
async def add_company(company: Company):
    try:
        company_key = f"company:{company.name}"
        redis_client.hmset(company_key, company.dict())
        return {"message": f"Company {company.name} added successfully"}
    except Exception as e:
        logger.error(f"Error adding company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/")
async def get_companies():
    try:
        companies = []
        for key in redis_client.scan_iter("company:*"):
            company_data = redis_client.hgetall(key)
            companies.append({
                k.decode(): v.decode() 
                for k, v in company_data.items()
            })
        return companies
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/companies/{company_name}")
async def delete_company(company_name: str):
    try:
        company_key = f"company:{company_name}"
        if redis_client.exists(company_key):
            redis_client.delete(company_key)
            return {"message": f"Company {company_name} deleted successfully"}
        raise HTTPException(status_code=404, detail="Company not found")
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Iniciar la aplicación
if __name__ == "__main__":
    # Iniciar scheduler
    scheduler.start()
    
    # Iniciar FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)