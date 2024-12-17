from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ..models.property import Property, PropertyStatus, PropertyType
from ..schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyFilter
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
        Get a list of properties with optional filtering
        """
        query = select(Property)
        
        # Aplicar filtros base
        if user_id:
            query = query.where(Property.user_id == user_id)
            
        if filters:
            for field, value in filters.items():
                if value is not None:
                    if field == 'city':
                        query = query.where(Property.city.ilike(f"%{value}%"))
                    elif field == 'state':
                        query = query.where(Property.state.ilike(f"%{value}%"))
                    elif field == 'status':
                        query = query.where(Property.status == value)
                    elif field == 'property_type':
                        query = query.where(Property.property_type == value)
                    elif field == 'bedrooms':
                        query = query.where(Property.bedrooms == value)
                    elif field == 'bathrooms':
                        query = query.where(Property.bathrooms == value)
                    elif field == 'parent_property_id':
                        query = query.where(Property.parent_property_id == value)
                    else:
                        query = query.where(getattr(Property, field) == value)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar consulta
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_property(self, property_id: int, user_id: str | None = None) -> Property:
        """
        Get a single property by ID
        """
        query = select(Property).where(Property.id == property_id)
        if user_id:
            query = query.where(Property.user_id == user_id)
            
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
        Create a new property
        """
        # Validar que si es una unidad, tenga parent_property_id
        if property_data.property_type == PropertyType.UNIT.value and not property_data.parent_property_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Units must have a parent property"
            )
            
        # Validar que si tiene parent_property_id, el parent exista y sea PRINCIPAL
        if property_data.parent_property_id:
            parent = await self.get_property(property_data.parent_property_id)
            if parent.property_type != PropertyType.PRINCIPAL.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent property must be of type PRINCIPAL"
                )
                
        # Crear la propiedad
        db_property = Property(
            **property_data.model_dump(),
            user_id=user_id
        )
        self.db.add(db_property)
        await self.db.commit()
        await self.db.refresh(db_property)
        return db_property

    async def update_property(
        self,
        property_id: int,
        property_data: PropertyUpdate,
        user_id: str | None = None
    ) -> Property:
        """
        Update a property
        """
        # Obtener la propiedad existente
        property = await self.get_property(property_id, user_id)
        
        # Validar cambios de tipo de propiedad
        if property_data.property_type:
            # Si cambia a UNIT, debe tener parent
            if property_data.property_type == PropertyType.UNIT.value:
                if not (property_data.parent_property_id or property.parent_property_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Units must have a parent property"
                    )
            # Si cambia a PRINCIPAL, no debe tener parent
            elif property_data.property_type == PropertyType.PRINCIPAL.value:
                property_data.parent_property_id = None
                
        # Validar parent_property_id si se proporciona
        if property_data.parent_property_id:
            parent = await self.get_property(property_data.parent_property_id)
            if parent.property_type != PropertyType.PRINCIPAL.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent property must be of type PRINCIPAL"
                )
                
        # Actualizar la propiedad
        property_data_dict = property_data.model_dump(exclude_unset=True)
        for key, value in property_data_dict.items():
            setattr(property, key, value)
            
        await self.db.commit()
        await self.db.refresh(property)
        return property

    async def delete_property(self, property_id: int, user_id: str | None = None) -> Property:
        """
        Delete a property
        """
        # Obtener la propiedad
        property = await self.get_property(property_id, user_id)
        
        # Verificar que no tenga unidades si es PRINCIPAL
        if property.property_type == PropertyType.PRINCIPAL.value:
            units_query = select(Property).where(Property.parent_property_id == property_id)
            result = await self.db.execute(units_query)
            if result.first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete a principal property with units. Delete the units first."
                )
        
        # Eliminar la propiedad
        await self.db.delete(property)
        await self.db.commit()
        return property

    async def get_units(self, property_id: int, user_id: str | None = None) -> List[Property]:
        """
        Get all units for a principal property
        """
        # Verificar que la propiedad principal existe
        property = await self.get_property(property_id, user_id)
        
        # Verificar que es una propiedad principal
        if property.property_type != PropertyType.PRINCIPAL.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only get units for a principal property"
            )
            
        # Obtener las unidades
        query = select(Property).where(Property.parent_property_id == property_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_parent_property(self, property_id: int, user_id: str | None = None) -> Property:
        """
        Get the parent property of a unit
        """
        # Obtener la unidad
        property = await self.get_property(property_id, user_id)
        
        # Verificar que es una unidad
        if property.property_type != PropertyType.UNIT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only get parent for a unit"
            )
            
        # Verificar que tiene parent_property_id
        if not property.parent_property_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit has no parent property"
            )
            
        # Obtener la propiedad principal
        return await self.get_property(property.parent_property_id, user_id)
