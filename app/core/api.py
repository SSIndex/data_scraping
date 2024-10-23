from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional
import redis
from datetime import datetime
import logging
from pydantic import BaseModel
from config.settings import REDIS_CONFIG, EXECUTION_INTERVALS
import json

# Configurar logging
logger = logging.getLogger(__name__)

# Modelos de datos
class Company(BaseModel):
    name: str
    country: str
    active: bool = True

class CollectorStatus(BaseModel):
    collector: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str

class CompanyUpdate(BaseModel):
    country: Optional[str]
    active: Optional[bool]

# Crear aplicación FastAPI
app = FastAPI(title="Data Collector API")

# Redis connection
def get_redis():
    return redis.Redis(**REDIS_CONFIG)

@app.post("/companies/", response_model=dict)
async def add_company(company: Company, redis_client: redis.Redis = Depends(get_redis)):
    """Añade una nueva empresa para recolección de datos"""
    try:
        company_key = f"company:{company.name}"
        if redis_client.exists(company_key):
            raise HTTPException(status_code=400, detail="Company already exists")
            
        redis_client.hmset(company_key, company.dict())
        return {"message": f"Company {company.name} added successfully"}
    except Exception as e:
        logger.error(f"Error adding company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/", response_model=List[dict])
async def get_companies(redis_client: redis.Redis = Depends(get_redis)):
    """Obtiene la lista de todas las empresas"""
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

@app.get("/companies/{company_name}", response_model=dict)
async def get_company(company_name: str, redis_client: redis.Redis = Depends(get_redis)):
    """Obtiene detalles de una empresa específica"""
    try:
        company_key = f"company:{company_name}"
        if not redis_client.exists(company_key):
            raise HTTPException(status_code=404, detail="Company not found")
            
        company_data = redis_client.hgetall(company_key)
        return {
            k.decode(): v.decode() 
            for k, v in company_data.items()
        }
    except Exception as e:
        logger.error(f"Error getting company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/companies/{company_name}", response_model=dict)
async def update_company(
    company_name: str, 
    company_update: CompanyUpdate,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Actualiza los detalles de una empresa"""
    try:
        company_key = f"company:{company_name}"
        if not redis_client.exists(company_key):
            raise HTTPException(status_code=404, detail="Company not found")
            
        update_data = company_update.dict(exclude_unset=True)
        if update_data:
            redis_client.hmset(company_key, update_data)
            
        return {"message": f"Company {company_name} updated successfully"}
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/companies/{company_name}")
async def delete_company(company_name: str, redis_client: redis.Redis = Depends(get_redis)):
    """Elimina una empresa"""
    try:
        company_key = f"company:{company_name}"
        if not redis_client.exists(company_key):
            raise HTTPException(status_code=404, detail="Company not found")
            
        redis_client.delete(company_key)
        return {"message": f"Company {company_name} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collectors/status", response_model=List[CollectorStatus])
async def get_collectors_status(redis_client: redis.Redis = Depends(get_redis)):
    """Obtiene el estado de todos los collectors"""
    try:
        collectors_status = []
        last_runs = redis_client.hgetall('collector_last_runs')
        
        for collector, interval in EXECUTION_INTERVALS.items():
            last_run = None
            next_run = None
            status = "Unknown"
            
            if collector.encode() in last_runs:
                last_run = datetime.fromtimestamp(float(last_runs[collector.encode()]))
                next_run = last_run.timestamp() + (interval * 3600)
                
                if datetime.now().timestamp() < next_run:
                    status = "Waiting"
                else:
                    status = "Ready"
            
            collectors_status.append(CollectorStatus(
                collector=collector,
                last_run=last_run,
                next_run=datetime.fromtimestamp(next_run) if next_run else None,
                status=status
            ))
            
        return collectors_status
    except Exception as e:
        logger.error(f"Error getting collectors status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collectors/{collector_name}/force-run")
async def force_collector_run(collector_name: str, redis_client: redis.Redis = Depends(get_redis)):
    """Fuerza la ejecución inmediata de un collector"""
    try:
        if collector_name not in EXECUTION_INTERVALS:
            raise HTTPException(status_code=404, detail="Collector not found")
            
        # Resetear el último tiempo de ejecución
        redis_client.hdel('collector_last_runs', collector_name)
        return {"message": f"Collector {collector_name} will run on next cycle"}
    except Exception as e:
        logger.error(f"Error forcing collector run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))