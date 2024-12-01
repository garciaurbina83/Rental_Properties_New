import pytest
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.crud import crud_payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.models.payment import PaymentStatus, PaymentConcept
from app.tests.utils.payment import create_random_payment
from app.tests.utils.user import create_random_user
from app.tests.utils.contract import create_random_contract

def test_create_payment(db: Session) -> None:
    amount = 1000.0
    payment_date = date.today()
    contract = create_random_contract(db)
    tenant = create_random_user(db)
    
    payment_in = PaymentCreate(
        amount=amount,
        payment_date=payment_date,
        concept=PaymentConcept.RENT,
        status=PaymentStatus.PENDING,
        contract_id=contract.id,
        tenant_id=tenant.id
    )
    payment = crud_payment.create(db=db, obj_in=payment_in)
    assert payment.amount == amount
    assert payment.payment_date == payment_date
    assert payment.status == PaymentStatus.PENDING
    assert payment.contract_id == contract.id
    assert payment.tenant_id == tenant.id

def test_get_payment(db: Session) -> None:
    payment = create_random_payment(db)
    stored_payment = crud_payment.get(db=db, id=payment.id)
    assert stored_payment
    assert payment.id == stored_payment.id
    assert payment.amount == stored_payment.amount
    assert payment.status == stored_payment.status

def test_update_payment(db: Session) -> None:
    payment = create_random_payment(db)
    new_amount = 2000.0
    payment_update = PaymentUpdate(amount=new_amount)
    payment2 = crud_payment.update(db=db, db_obj=payment, obj_in=payment_update)
    assert payment.id == payment2.id
    assert payment2.amount == new_amount
    assert payment.payment_date == payment2.payment_date

def test_delete_payment(db: Session) -> None:
    payment = create_random_payment(db)
    payment2 = crud_payment.remove(db=db, id=payment.id)
    payment3 = crud_payment.get(db=db, id=payment.id)
    assert payment3 is None
    assert payment2.id == payment.id
    assert payment2.amount == payment.amount

def test_get_multi_payment(db: Session) -> None:
    payment1 = create_random_payment(db)
    payment2 = create_random_payment(db)
    stored_payments = crud_payment.get_multi(db=db)
    assert len(stored_payments) >= 2
    assert any(p.id == payment1.id for p in stored_payments)
    assert any(p.id == payment2.id for p in stored_payments)

def test_get_payments_by_status(db: Session) -> None:
    payment1 = create_random_payment(db, status=PaymentStatus.PAID)
    payment2 = create_random_payment(db, status=PaymentStatus.PENDING)
    
    paid_payments = crud_payment.get_by_status(db=db, status=PaymentStatus.PAID)
    assert all(p.status == PaymentStatus.PAID for p in paid_payments)
    assert any(p.id == payment1.id for p in paid_payments)
    
    pending_payments = crud_payment.get_by_status(db=db, status=PaymentStatus.PENDING)
    assert all(p.status == PaymentStatus.PENDING for p in pending_payments)
    assert any(p.id == payment2.id for p in pending_payments)

def test_get_payments_by_date_range(db: Session) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    payment1 = create_random_payment(db, payment_date=yesterday)
    payment2 = create_random_payment(db, payment_date=today)
    payment3 = create_random_payment(db, payment_date=tomorrow)
    
    # Probar rango de fechas
    payments = crud_payment.get_by_date_range(
        db=db,
        start_date=yesterday,
        end_date=today
    )
    payment_dates = [p.payment_date for p in payments]
    assert all(yesterday <= d <= today for d in payment_dates)
    assert any(p.id == payment1.id for p in payments)
    assert any(p.id == payment2.id for p in payments)
    assert not any(p.id == payment3.id for p in payments)

def test_get_payments_by_contract(db: Session) -> None:
    contract = create_random_contract(db)
    payment1 = create_random_payment(db, contract_id=contract.id)
    payment2 = create_random_payment(db, contract_id=contract.id)
    
    contract_payments = crud_payment.get_by_contract(db=db, contract_id=contract.id)
    assert len(contract_payments) >= 2
    assert all(p.contract_id == contract.id for p in contract_payments)
    assert any(p.id == payment1.id for p in contract_payments)
    assert any(p.id == payment2.id for p in contract_payments)

def test_get_payments_by_tenant(db: Session) -> None:
    tenant = create_random_user(db)
    payment1 = create_random_payment(db, tenant_id=tenant.id)
    payment2 = create_random_payment(db, tenant_id=tenant.id)
    
    tenant_payments = crud_payment.get_by_tenant(db=db, tenant_id=tenant.id)
    assert len(tenant_payments) >= 2
    assert all(p.tenant_id == tenant.id for p in tenant_payments)
    assert any(p.id == payment1.id for p in tenant_payments)
    assert any(p.id == payment2.id for p in tenant_payments)
