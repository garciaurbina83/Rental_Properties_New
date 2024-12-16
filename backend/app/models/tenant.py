from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    lease_start = Column(Date, nullable=False)
    lease_end = Column(Date, nullable=False)
    deposit = Column(Numeric(10, 2), nullable=False)
    monthly_rent = Column(Numeric(10, 2), nullable=False)
    payment_day = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    property = relationship("Property", back_populates="tenants")

    class Config:
        orm_mode = True
