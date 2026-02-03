import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.database import AsyncSessionLocal
from src.domain.models import Rate

async def seed_rates():
    async with AsyncSessionLocal() as db:
        print("Seeding Rates...")
        
        # Limpiar tabla rates
        await db.execute(text("TRUNCATE TABLE rates RESTART IDENTITY CASCADE"))
        
        dummy_rates = [
            # RIMAC
            Rate(insurer="Rimac", plan_name="Todo Riesgo", brand="Toyota", model="Corolla", year_min=2015, year_max=2025, usage="Particular", base_price=650.0),
            Rate(insurer="Rimac", plan_name="Todo Riesgo", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=580.0),
            Rate(insurer="Rimac", plan_name="Responsabilidad Civil", brand="Toyota", model="Corolla", year_min=2010, year_max=2025, usage="Particular", base_price=200.0),
            
            # PACIFICO
            Rate(insurer="Pacifico", plan_name="Plan Km", brand="Toyota", model="Corolla", year_min=2018, year_max=2025, usage="Particular", base_price=450.0),
            Rate(insurer="Pacifico", plan_name="Todo Riesgo", brand="Kia", model="Sportage", year_min=2020, year_max=2025, usage="Particular", base_price=900.0),
            
            # MAPFRE
            Rate(insurer="Mapfre", plan_name="Dorada", brand="Hyundai", model="Tucson", year_min=2019, year_max=2025, usage="Particular", base_price=850.0),
        ]
        
        db.add_all(dummy_rates)
        await db.commit()
        print(f"Added {len(dummy_rates)} rates.")

if __name__ == "__main__":
    asyncio.run(seed_rates())
