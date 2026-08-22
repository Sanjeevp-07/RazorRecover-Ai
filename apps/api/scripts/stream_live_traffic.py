import sys
import uuid
import random
import asyncio
import time
from pathlib import Path

# Ensure app package is in python path
sys.path.insert(0, str(Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.core.db import AsyncSessionLocal
from app.core.config import settings
from app.models import Merchant, Customer, Order, OrderStatus, Payment, PaymentStatus, RecoveryCase, RecoveryCaseStatus
from app.services.recovery_orchestrator import RecoveryOrchestrator

DEMO_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

LIVE_STREAM_PROFILES = [
    {
        "label": "🚨 CARD TESTING HACKER ANOMALY",
        "reason": "Rapid card velocity limit exceeded: 8 declines in 45s across proxy IP",
        "method": "card",
        "amount_minor": 85000,
        "customer": "dark_anon@tempmail.ninja"
    },
    {
        "label": "⚡ TRANSIENT HDFC BANK SWITCH DROPOFF",
        "reason": "Issuer bank network timeout (504 Gateway Timeout)",
        "method": "upi",
        "amount_minor": 450000,
        "customer": "priya.patel@corp.in"
    },
    {
        "label": "🐳 HIGH VALUE ENTERPRISE TRANSACTION",
        "reason": "High-value transaction step-up auth timeout",
        "method": "netbanking",
        "amount_minor": 12500000,
        "customer": "vikram@singhania-holdings.com"
    },
    {
        "label": "💬 INSUFFICIENT BALANCE RECOVERY",
        "reason": "Insufficient balance on primary card",
        "method": "card",
        "amount_minor": 280000,
        "customer": "aarav.sharma@example.com"
    }
]

async def stream_live_events(num_events: int = 5, delay_seconds: int = 3):
    print("\n=======================================================")
    print(f"🔴 STREAMING {num_events} LIVE REAL-WORLD EVENTS (NVIDIA NIM AI)")
    print(f"=======================================================\n")

    async with AsyncSessionLocal() as session:
        for i in range(1, num_events + 1):
            event = random.choice(LIVE_STREAM_PROFILES)
            case_id = uuid.uuid4()
            order_id = uuid.uuid4()
            payment_id = uuid.uuid4()
            correlation_id = uuid.uuid4()

            print(f"[{i}/{num_events}] INGESTING EVENT: {event['label']}")
            print(f"  • Customer: {event['customer']}")
            print(f"  • Amount: ₹{event['amount_minor'] / 100:,.2f}")
            print(f"  • Failure Reason: {event['reason']}")

            # Create records in DB
            cust_id = uuid.uuid4()
            customer = Customer(
                id=cust_id,
                merchant_id=DEMO_MERCHANT_ID,
                email=f"live_{i}_{event['customer']}",
                phone="+919876543210",
                name=f"Live Customer #{i}"
            )
            session.add(customer)

            order = Order(
                id=order_id,
                merchant_id=DEMO_MERCHANT_ID,
                customer_id=cust_id,
                amount_minor=event["amount_minor"],
                currency="INR",
                status=OrderStatus.FAILED
            )
            session.add(order)

            payment = Payment(
                id=payment_id,
                merchant_id=DEMO_MERCHANT_ID,
                order_id=order_id,
                amount_minor=event["amount_minor"],
                currency="INR",
                status=PaymentStatus.FAILED,
                failure_reason=event["reason"],
                method=event["method"]
            )
            session.add(payment)

            case = RecoveryCase(
                id=case_id,
                merchant_id=DEMO_MERCHANT_ID,
                payment_id=payment_id,
                status=RecoveryCaseStatus.OPEN,
                correlation_id=correlation_id
            )
            session.add(case)
            await session.commit()

            print(f"  🤖 Triggering AI Reasoner & Policy Engine for Case {case_id}...")
            start_t = time.time()

            orchestrator = RecoveryOrchestrator(session, DEMO_MERCHANT_ID)
            updated_case = await orchestrator.execute_recovery_pipeline(case_id)
            duration = round(time.time() - start_t, 2)

            print(f"  🎯 RESULT ({duration}s): Status -> {updated_case.status.value}")
            print("-------------------------------------------------------")

            if i < num_events:
                await asyncio.sleep(delay_seconds)

    print("\n✅ Live stream simulation finished! Check your dashboard at http://localhost:3000\n")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    asyncio.run(stream_live_events(num_events=count))
