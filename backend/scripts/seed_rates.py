import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.core.database import AsyncSessionLocal
from src.domain.models import Rate

async def seed_rates():
    async with AsyncSessionLocal() as db:
        print("Seeding Rates...")
        
        # Limpiar tabla rates
        await db.execute(text("TRUNCATE TABLE rates RESTART IDENTITY CASCADE"))
        
        dummy_rates = [
            # --- TOYOTA YARIS (Comparativa) ---
            Rate(insurer="Rimac", plan_name="Todo Riesgo Plata", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=580.0, variable_rate=0.035),
            Rate(insurer="Pacifico", plan_name="Plan Kilómetros", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=420.0, variable_rate=0.025),
            Rate(insurer="Mapfre", plan_name="Póliza Dorada", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=600.0, variable_rate=0.038),
            Rate(insurer="La Positiva", plan_name="Auto Total", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=550.0, variable_rate=0.032),
            Rate(insurer="Qualitas", plan_name="Paquete Amplia", brand="Toyota", model="Yaris", year_min=2015, year_max=2025, usage="Particular", base_price=530.0, variable_rate=0.03),
            # Taxi Yaris
            Rate(insurer="Rimac", plan_name="Taxi Seguro", brand="Toyota", model="Yaris", year_min=2012, year_max=2025, usage="Taxi", base_price=950.0, variable_rate=0.06),
            Rate(insurer="Pacifico", plan_name="Taxi Full", brand="Toyota", model="Yaris", year_min=2012, year_max=2025, usage="Taxi", base_price=920.0, variable_rate=0.058),

            # --- TOYOTA COROLLA (Comparativa) ---
            Rate(insurer="Rimac", plan_name="Todo Riesgo Black", brand="Toyota", model="Corolla", year_min=2015, year_max=2025, usage="Particular", base_price=650.0, variable_rate=0.04),
            Rate(insurer="Pacifico", plan_name="Todo Riesgo Full", brand="Toyota", model="Corolla", year_min=2015, year_max=2025, usage="Particular", base_price=670.0, variable_rate=0.042),
            Rate(insurer="Mapfre", plan_name="Póliza Trébol", brand="Toyota", model="Corolla", year_min=2015, year_max=2025, usage="Particular", base_price=620.0, variable_rate=0.039),
            Rate(insurer="La Positiva", plan_name="Auto Total", brand="Toyota", model="Corolla", year_min=2015, year_max=2025, usage="Particular", base_price=640.0, variable_rate=0.04),

            # --- KIA SPORTAGE (Comparativa) ---
            Rate(insurer="Rimac", plan_name="Todo Riesgo Camioneta", brand="Kia", model="Sportage", year_min=2015, year_max=2025, usage="Particular", base_price=950.0, variable_rate=0.045),
            Rate(insurer="Pacifico", plan_name="Todo Riesgo Full", brand="Kia", model="Sportage", year_min=2015, year_max=2025, usage="Particular", base_price=900.0, variable_rate=0.045),
            Rate(insurer="Mapfre", plan_name="Póliza Dorada", brand="Kia", model="Sportage", year_min=2015, year_max=2025, usage="Particular", base_price=920.0, variable_rate=0.044),
            Rate(insurer="La Positiva", plan_name="Camioneta Segura", brand="Kia", model="Sportage", year_min=2015, year_max=2025, usage="Particular", base_price=880.0, variable_rate=0.043),

            # --- HYUNDAI TUCSON (Comparativa) ---
            Rate(insurer="Rimac", plan_name="Todo Riesgo Camioneta", brand="Hyundai", model="Tucson", year_min=2015, year_max=2025, usage="Particular", base_price=940.0, variable_rate=0.045),
            Rate(insurer="Mapfre", plan_name="Póliza Dorada", brand="Hyundai", model="Tucson", year_min=2019, year_max=2025, usage="Particular", base_price=850.0, variable_rate=0.04),
            Rate(insurer="Qualitas", plan_name="Paquete Amplia", brand="Hyundai", model="Tucson", year_min=2015, year_max=2025, usage="Particular", base_price=890.0, variable_rate=0.042),

            # --- OTROS ---
            Rate(insurer="Rimac", plan_name="Responsabilidad Civil", brand="Toyota", model="Hilux", year_min=2010, year_max=2025, usage="Particular", base_price=250.0, variable_rate=0.01),
            Rate(insurer="Rimac", plan_name="Carga Ligera", brand="Hyundai", model="H1", year_min=2015, year_max=2025, usage="Comercial", base_price=1100.0, variable_rate=0.055),
            Rate(insurer="Pacifico", plan_name="Todo Riesgo", brand="Mazda", model="CX-5", year_min=2019, year_max=2025, usage="Particular", base_price=950.0, variable_rate=0.045),
            Rate(insurer="Mapfre", plan_name="Auto Elite", brand="Nissan", model="Versa", year_min=2018, year_max=2025, usage="Particular", base_price=700.0, variable_rate=0.038),
            Rate(insurer="La Positiva", plan_name="Auto Total", brand="Chevrolet", model="Spark", year_min=2015, year_max=2025, usage="Particular", base_price=500.0, variable_rate=0.035),
            Rate(insurer="La Positiva", plan_name="Camión Seguro", brand="Nissan", model="Frontier", year_min=2010, year_max=2025, usage="Carga", base_price=1500.0, variable_rate=0.08),
        
        
            # Kia Picanto (Muy común, competencia fuerte)
            Rate(insurer="Rimac", plan_name="Plan Web Digital", brand="Kia", model="Picanto", year_min=2018, year_max=2025, usage="Particular", base_price=380.0, variable_rate=0.03),
            Rate(insurer="Pacifico", plan_name="Plan Kilómetros", brand="Kia", model="Picanto", year_min=2018, year_max=2025, usage="Particular", base_price=350.0, variable_rate=0.028),
            Rate(insurer="La Positiva", plan_name="Auto Total", brand="Kia", model="Picanto", year_min=2018, year_max=2025, usage="Particular", base_price=400.0, variable_rate=0.032),
            
            # Hyundai Grand i10
            Rate(insurer="Qualitas", plan_name="Pack Estándar", brand="Hyundai", model="Grand i10", year_min=2019, year_max=2025, usage="Particular", base_price=390.0, variable_rate=0.031),
            Rate(insurer="Mapfre", plan_name="Póliza Dorada", brand="Hyundai", model="Grand i10", year_min=2019, year_max=2025, usage="Particular", base_price=410.0, variable_rate=0.033),

            # --- PICKUPS (Alto Riesgo de Robo en Perú - Tasas altas) ---
            # Toyota Hilux (Ampliando opciones)
            Rate(insurer="Pacifico", plan_name="Todo Riesgo 4x4", brand="Toyota", model="Hilux", year_min=2015, year_max=2025, usage="Particular", base_price=1200.0, variable_rate=0.075), # Tasa alta 7.5%
            Rate(insurer="Mapfre", plan_name="Póliza 4x4", brand="Toyota", model="Hilux", year_min=2015, year_max=2025, usage="Particular", base_price=1150.0, variable_rate=0.072),
            Rate(insurer="La Positiva", plan_name="Camioneta Rural", brand="Toyota", model="Hilux", year_min=2015, year_max=2025, usage="Comercial", base_price=1400.0, variable_rate=0.085), # Uso comercial

            # Mitsubishi L200
            Rate(insurer="Rimac", plan_name="Carga Segura", brand="Mitsubishi", model="L200", year_min=2016, year_max=2025, usage="Particular", base_price=1100.0, variable_rate=0.065),
            Rate(insurer="Qualitas", plan_name="Pickups", brand="Mitsubishi", model="L200", year_min=2016, year_max=2025, usage="Particular", base_price=1050.0, variable_rate=0.060),

            # --- SUVs CHINAS (Mercado en crecimiento) ---
            # Chery Tiggo 7
            Rate(insurer="Rimac", plan_name="Todo Riesgo", brand="Chery", model="Tiggo 7", year_min=2020, year_max=2025, usage="Particular", base_price=600.0, variable_rate=0.045),
            Rate(insurer="Pacifico", plan_name="Plan Base", brand="Chery", model="Tiggo 7", year_min=2020, year_max=2025, usage="Particular", base_price=580.0, variable_rate=0.042),

            # Changan CS35
            Rate(insurer="La Positiva", plan_name="Auto Total", brand="Changan", model="CS35", year_min=2019, year_max=2025, usage="Particular", base_price=550.0, variable_rate=0.040),
            
            # --- ALTA GAMA (Primas base altas, tasas a veces menores) ---
            # BMW X1
            Rate(insurer="Rimac", plan_name="VIP Black", brand="BMW", model="X1", year_min=2018, year_max=2025, usage="Particular", base_price=1500.0, variable_rate=0.025), # Tasa baja, precio base alto
            Rate(insurer="Pacifico", plan_name="Signature", brand="BMW", model="X1", year_min=2018, year_max=2025, usage="Particular", base_price=1450.0, variable_rate=0.024),

            # Audi Q3
            Rate(insurer="Mapfre", plan_name="Póliza Platinum", brand="Audi", model="Q3", year_min=2018, year_max=2025, usage="Particular", base_price=1400.0, variable_rate=0.026),

            # --- USO TAXI (Mercado específico) ---
            # Kia Soluto (Taxi)
            Rate(insurer="La Positiva", plan_name="Taxi Seguro", brand="Kia", model="Soluto", year_min=2019, year_max=2025, usage="Taxi", base_price=850.0, variable_rate=0.055),
            Rate(insurer="Rimac", plan_name="Taxi Digital", brand="Kia", model="Soluto", year_min=2019, year_max=2025, usage="Taxi", base_price=880.0, variable_rate=0.058),
            
            # Nissan Versa (Taxi)
            Rate(insurer="Pacifico", plan_name="Taxi Full", brand="Nissan", model="Versa", year_min=2015, year_max=2025, usage="Taxi", base_price=900.0, variable_rate=0.052),
        ]
        
        db.add_all(dummy_rates)
        await db.commit()
        print(f"Added {len(dummy_rates)} rates.")

if __name__ == "__main__":
    asyncio.run(seed_rates())
