from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus, PaymentConcept
from app.tests.utils.user import create_random_user
from app.tests.utils.contract import create_random_contract
from app.tests.utils.utils import random_lower_string

def create_random_payment(
    db: Session,
    *,
    status: Optional[PaymentStatus] = None,
    payment_date: Optional[date] = None,
    contract_id: Optional[int] = None,
    tenant_id: Optional[int] = None
) -> Payment:
    if contract_id is None:
        contract = create_random_contract(db)
        contract_id = contract.id
    
    if tenant_id is None:
        tenant = create_random_user(db)
        tenant_id = tenant.id
    
    if status is None:
        status = PaymentStatus.PENDING
    
    if payment_date is None:
        payment_date = date.today()
    
    payment = Payment(
        amount=1000.0,  # monto aleatorio
        payment_date=payment_date,
        concept=PaymentConcept.RENT,
        status=status,
        contract_id=contract_id,
        tenant_id=tenant_id,
        description=random_lower_string()
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
