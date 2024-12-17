from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, validates
from ..core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True, nullable=False)
    lease_start = Column(Date, nullable=False)
    lease_end = Column(Date, nullable=False)
    deposit = Column(Numeric(10, 2), nullable=False)
    monthly_rent = Column(Numeric(10, 2), nullable=False)
    payment_day = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    property = relationship("Property", back_populates="tenants")

    def __repr__(self):
        return f"<Tenant {self.first_name} {self.last_name}>"

    @validates('payment_day')
    def validate_payment_day(self, key, value):
        """Validate that payment day is between 1 and 31"""
        if not 1 <= value <= 31:
            raise ValueError("Payment day must be between 1 and 31")
        return value

    @validates('lease_end')
    def validate_lease_end(self, key, value):
        """Validate that lease end is after lease start"""
        if hasattr(self, 'lease_start') and value < self.lease_start:
            raise ValueError("Lease end must be after lease start")
        return value
