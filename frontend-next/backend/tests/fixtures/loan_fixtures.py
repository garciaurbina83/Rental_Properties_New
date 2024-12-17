from datetime import date, datetime, timedelta
from app.models import (
    LoanType, LoanStatus, 
    PaymentMethod, PaymentStatus
)

def loan_fixture():
    return {
        "property_id": 1,
        "loan_type": LoanType.MORTGAGE,
        "principal_amount": 100000.0,
        "interest_rate": 5.5,
        "term_months": 240,  # 20 años
        "payment_day": 5,
        "start_date": date.today(),
        "lender_name": "Banco Test",
        "lender_contact": "contact@bancotest.com",
        "loan_number": "TEST-2024-001",
        "notes": "Préstamo de prueba"
    }

def loan_document_fixture():
    return {
        "document_type": "CONTRATO",
        "file_path": "/test/path/contract.pdf",
        "description": "Contrato de préstamo hipotecario"
    }

def loan_payment_fixture():
    return {
        "payment_date": date.today(),
        "due_date": date.today(),
        "amount": 1000.0,
        "payment_method": PaymentMethod.TRANSFER,
        "reference_number": "REF-001",
        "late_fee": 0.0,
        "notes": "Pago mensual regular"
    }

def processed_payment_fixture():
    payment = loan_payment_fixture()
    payment.update({
        "principal_amount": 750.0,
        "interest_amount": 250.0,
        "status": PaymentStatus.COMPLETED,
        "processed_by": 1,
        "processed_at": datetime.utcnow()
    })
    return payment

def loan_with_payments_fixture():
    loan = loan_fixture()
    loan.update({
        "end_date": date.today() + timedelta(days=30*240),
        "status": LoanStatus.ACTIVE,
        "remaining_balance": 100000.0,
        "monthly_payment": 687.89,
        "last_payment_date": None,
        "next_payment_date": date.today() + timedelta(days=30)
    })
    return loan

def amortization_schedule_fixture():
    return [
        {
            "payment_number": 1,
            "payment_date": date.today() + timedelta(days=30),
            "payment_amount": 687.89,
            "principal_payment": 437.89,
            "interest_payment": 250.00,
            "remaining_balance": 99562.11
        },
        {
            "payment_number": 2,
            "payment_date": date.today() + timedelta(days=60),
            "payment_amount": 687.89,
            "principal_payment": 438.99,
            "interest_payment": 248.90,
            "remaining_balance": 99123.12
        }
    ]

def loan_summary_fixture():
    return {
        "loan_id": 1,
        "total_amount": 100000.0,
        "remaining_balance": 99123.12,
        "total_paid": 1375.78,
        "total_principal_paid": 876.88,
        "total_interest_paid": 498.90,
        "total_late_fees": 0.0,
        "monthly_payment": 687.89,
        "next_payment_date": date.today() + timedelta(days=90),
        "next_payment_amount": 687.89,
        "status": LoanStatus.ACTIVE,
        "payments_made": 2,
        "remaining_payments": 238
    }
