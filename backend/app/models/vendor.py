from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Vendor(BaseModel):
    __tablename__ = "vendors"

    # Información básica
    name = Column(String, nullable=False)
    business_type = Column(String)
    tax_id = Column(String)
    contact_person = Column(String)
    
    # Información de contacto
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    website = Column(String, nullable=True)
    
    # Detalles bancarios
    bank_name = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    payment_terms = Column(String, nullable=True)
    
    # Estado y verificación
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # Rating interno del proveedor (1-5)
    
    # Notas y documentos
    notes = Column(Text, nullable=True)
    documents_path = Column(String, nullable=True)  # Ruta a documentos del proveedor
    
    # Relaciones
    expenses = relationship("Expense", back_populates="vendor")
    
    def __repr__(self):
        return f"<Vendor {self.name}>"
