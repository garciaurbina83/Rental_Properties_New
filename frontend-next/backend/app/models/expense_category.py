from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class ExpenseCategory(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("expensecategory.id"), nullable=True)
    
    # Relationships
    parent = relationship("ExpenseCategory", remote_side=[id], back_populates="children")
    children = relationship("ExpenseCategory", back_populates="parent")
    expenses = relationship("Expense", back_populates="category")
