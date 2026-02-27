from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..domain.models import Policy, Rate, Quote, Customer
from ..domain.schemas import QuoteRequest, QuoteResponse

class QuoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quotes(self, request: QuoteRequest) -> list[QuoteResponse]:
        """
        Calcula cotizaciones usando el tarifario 'Rate'.
        Gestiona la creación/actualización del Cliente si se proporciona DNI.
        """
        # 1. Gestión de Cliente (si hay DNI)
        customer_id = None
        if request.dni:
            # Buscar si existe
            result = await self.db.execute(select(Customer).where(Customer.dni == request.dni))
            customer = result.scalars().first()
            
            if not customer:
                # Crear nuevo
                customer = Customer(
                    dni=request.dni,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    email=request.email,
                    phone=request.phone
                )
                self.db.add(customer)
                await self.db.flush() # Para obtener el ID
            
            customer_id = customer.id

        # 2. Buscar tasas que coincidan con el vehículo
        car_brand = request.car_brand
        car_model = request.car_model
        car_year = request.car_year
        
        if request.vehicle:
            car_brand = request.vehicle.get('brand', car_brand)
            car_model = request.vehicle.get('model', car_model)
            car_year = request.vehicle.get('year', car_year)
            
        # Clean inputs
        car_brand = car_brand.strip() if car_brand else ""
        car_model = car_model.strip() if car_model else ""
        
        stmt = select(Rate).where(
            (Rate.brand.ilike(car_brand)) &
            (Rate.model.ilike(car_model)) &
            (Rate.year_min <= car_year) &
            (Rate.year_max >= car_year) &
            (Rate.usage.ilike(request.usage))
        )
        
        result = await self.db.execute(stmt)
        rates = result.scalars().all()
        
        quotes = []
        
        # Si no hay tasas exactas, podríamos tener una "Default" o devolver vacío
        if not rates:
            pass

        for rate in rates:
            # Lógica comercial real
            final_price = rate.base_price
            
            # Ajuste por edad
            if request.age < 25:
                final_price *= 1.2
            
            # Guardar el historial de cotización
            new_quote = Quote(
                customer_id=customer_id,
                customer_age=request.age,
                car_brand=car_brand,
                car_model=self.normalize_text(car_model),
                car_year=car_year,
                car_usage=request.usage,
                selected_insurer=rate.insurer,
                selected_plan=rate.plan_name,
                final_price=round(final_price, 2),
                status="generated"
            )
            self.db.add(new_quote)
            
            quotes.append(QuoteResponse(
                insurer=rate.insurer,
                plan_name=rate.plan_name,
                price=round(final_price, 2),
                coverage_summary=f"Plan {rate.plan_name} para {rate.brand} {rate.model}"
            ))
            
        # Commit para guardar el historial
        if quotes:
            await self.db.commit()
            
        return quotes

    def normalize_text(self, text: str) -> str:
        return text.strip().title() if text else ""
