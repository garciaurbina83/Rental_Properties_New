from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ..models.property import Property, PropertyStatus, PropertyType
from ..schemas.property import PropertyCreate, PropertyUpdate, PropertyWithUnits
from fastapi import HTTPException, status

class PropertyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_properties(
        self,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Property]:
        """
        Obtiene una lista de propiedades con filtros opcionales
        """
        query = select(Property).where(Property.is_active == True)
        
        if user_id:
            query = query.where(Property.user_id == user_id)
        
        if filters:
            conditions = []
            if 'status' in filters:
                try:
                    status_enum = PropertyStatus(filters['status'].lower())
                    conditions.append(Property.status == status_enum)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                    )
            if 'city' in filters:
                conditions.append(Property.city.ilike(f"%{filters['city']}%"))
            if 'min_price' in filters:
                conditions.append(Property.monthly_rent >= filters['min_price'])
            if 'max_price' in filters:
                conditions.append(Property.monthly_rent <= filters['max_price'])
            if 'bedrooms' in filters:
                conditions.append(Property.bedrooms >= filters['bedrooms'])
            if 'bathrooms' in filters:
                conditions.append(Property.bathrooms >= filters['bathrooms'])
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_property(self, property_id: int) -> Optional[Property]:
        """
        Obtiene una propiedad por su ID
        """
        query = select(Property).where(
            and_(
                Property.id == property_id,
                Property.is_active == True
            )
        )
        result = await self.db.execute(query)
        property = result.scalar_one_or_none()
        
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with id {property_id} not found"
            )
        return property

    async def create_property(self, property_data: PropertyCreate, user_id: str) -> Property:
        """
        Crea una nueva propiedad
        """
        # Validar tipo de propiedad y relaciones
        if property_data.property_type == PropertyType.UNIT:
            if not property_data.parent_property_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Units must have a parent property"
                )
            
            # Verificar que el padre existe y es una propiedad principal
            parent = await self.get_property(property_data.parent_property_id)
            if parent.property_type != PropertyType.PRINCIPAL:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Units can only be created under principal properties"
                )
        
        property_dict = property_data.model_dump()
        property_dict["user_id"] = user_id
        new_property = Property(**property_dict)
        
        self.db.add(new_property)
        await self.db.commit()
        await self.db.refresh(new_property)
        
        return new_property

    async def update_property(
        self,
        property_id: int,
        property_update: PropertyUpdate
    ) -> Property:
        """
        Actualiza una propiedad existente
        """
        property = await self.get_property(property_id)
        
        update_data = property_update.model_dump(exclude_unset=True)
        
        # Si se está actualizando el estado, validar el nuevo estado
        if "status" in update_data:
            try:
                update_data["status"] = PropertyStatus(update_data["status"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
        
        for key, value in update_data.items():
            setattr(property, key, value)
        
        await self.db.commit()
        await self.db.refresh(property)
        
        return property

    async def delete_property(self, property_id: int) -> bool:
        """
        Elimina una propiedad (soft delete)
        """
        property = await self.get_property(property_id)
        
        # Si es una propiedad principal, también desactivar sus unidades
        if property.property_type == PropertyType.PRINCIPAL:
            units_query = select(Property).where(
                and_(
                    Property.parent_property_id == property_id,
                    Property.is_active == True
                )
            )
            result = await self.db.execute(units_query)
            units = result.scalars().all()
            
            for unit in units:
                unit.is_active = False
        
        property.is_active = False
        await self.db.commit()
        return True

    async def get_property_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de las propiedades
        """
        # Total de propiedades activas
        total_query = select(func.count(Property.id)).where(Property.is_active == True)
        total_result = await self.db.execute(total_query)
        total_properties = total_result.scalar()
        
        # Propiedades por estado
        status_query = select(
            Property.status,
            func.count(Property.id)
        ).where(
            Property.is_active == True
        ).group_by(Property.status)
        status_result = await self.db.execute(status_query)
        status_counts = {status: count for status, count in status_result}
        
        # Valor total de las propiedades
        value_query = select(func.sum(Property.current_value)).where(Property.is_active == True)
        value_result = await self.db.execute(value_query)
        total_value = value_result.scalar() or 0
        
        return {
            "total_properties": total_properties,
            "status_distribution": status_counts,
            "total_value": total_value
        }

    async def search_properties(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Property]:
        """
        Búsqueda de propiedades por término
        """
        query = select(Property).where(
            and_(
                Property.is_active == True,
                or_(
                    Property.name.ilike(f"%{search_term}%"),
                    Property.address.ilike(f"%{search_term}%"),
                    Property.city.ilike(f"%{search_term}%"),
                    Property.state.ilike(f"%{search_term}%"),
                    Property.country.ilike(f"%{search_term}%")
                )
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_properties_by_status(
        self,
        status: PropertyStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Property]:
        """
        Obtiene propiedades por estado
        """
        query = select(Property).where(
            and_(
                Property.status == status,
                Property.is_active == True
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_property_status(
        self,
        property_id: int,
        new_status: PropertyStatus
    ) -> Property:
        """
        Actualiza el estado de una propiedad
        """
        property = await self.get_property(property_id)
        
        # Validar el nuevo estado
        try:
            status_enum = PropertyStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
            )
        
        property.status = status_enum
        await self.db.commit()
        await self.db.refresh(property)
        
        return property

    async def bulk_update_properties(
        self,
        property_ids: List[int],
        property_update: PropertyUpdate
    ) -> List[Property]:
        """
        Updates multiple properties at once
        """
        # Verificar que todas las propiedades existen
        properties = []
        for property_id in property_ids:
            property = await self.get_property(property_id)
            properties.append(property)
        
        update_data = property_update.model_dump(exclude_unset=True)
        
        # Si se está actualizando el estado, validar el nuevo estado
        if "status" in update_data:
            try:
                update_data["status"] = PropertyStatus(update_data["status"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in PropertyStatus]}"
                )
        
        # Actualizar cada propiedad
        for property in properties:
            for key, value in update_data.items():
                setattr(property, key, value)
        
        await self.db.commit()
        
        # Refrescar todas las propiedades
        for property in properties:
            await self.db.refresh(property)
        
        return properties

    async def create_unit(
        self,
        principal_id: int,
        unit_data: PropertyCreate,
        user_id: str
    ) -> Property:
        """
        Crea una nueva unidad asociada a una propiedad principal
        """
        # Asegurarse de que la propiedad principal existe y es del tipo correcto
        principal = await self.get_property(principal_id)
        if principal.property_type != PropertyType.PRINCIPAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Units can only be created under principal properties"
            )
        
        # Forzar el tipo de propiedad a UNIT y establecer el padre
        unit_data.property_type = PropertyType.UNIT
        unit_data.parent_property_id = principal_id
        
        # Crear la unidad
        return await self.create_property(unit_data, user_id)

    async def get_property_with_units(self, property_id: int) -> PropertyWithUnits:
        """
        Obtiene una propiedad con todas sus unidades
        """
        # Obtener la propiedad principal
        property = await self.get_property(property_id)
        
        # Verificar que es una propiedad principal
        if property.property_type != PropertyType.PRINCIPAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only principal properties can have units"
            )
        
        # Obtener las unidades asociadas
        units_query = select(Property).where(
            and_(
                Property.parent_property_id == property_id,
                Property.is_active == True
            )
        )
        result = await self.db.execute(units_query)
        units = result.scalars().all()
        
        # Crear y retornar el esquema PropertyWithUnits
        return PropertyWithUnits(
            **property.__dict__,
            units=units
        )

    async def get_units_by_principal(self, principal_id: int) -> List[Property]:
        """
        Obtiene todas las unidades de una propiedad principal
        """
        # Verificar que la propiedad principal existe y es del tipo correcto
        principal = await self.get_property(principal_id)
        if principal.property_type != PropertyType.PRINCIPAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only principal properties can have units"
            )
        
        # Obtener las unidades
        query = select(Property).where(
            and_(
                Property.parent_property_id == principal_id,
                Property.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
