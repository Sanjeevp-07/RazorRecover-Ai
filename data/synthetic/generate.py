import json
import uuid
import random

def generate_synthetic_cases():
    scenarios = [
        # (category, failure_reason, min_amt, max_amt, retry_count, score, velocity, expected_action, min_prob, max_prob, requires_human)
        ("temp_failure", "Payment expired during 3DS OTP verification", 50000, 300000, 1, 0.85, 0.98, False, "CREATE_PAYMENT_LINK", 0.85, 0.95, False),
        ("temp_failure", "Issuer bank network timeout", 100000, 450000, 1, 0.80, 0.95, False, "CREATE_PAYMENT_LINK", 0.90, 0.98, False),
        ("temp_failure", "Temporary gateway communication failure", 80000, 250000, 0, 0.82, 0.95, False, "CREATE_PAYMENT_LINK", 0.88, 0.96, False),
        ("repeated_failure", "Exceeded maximum retry attempts at bank", 150000, 400000, 4, 0.20, 0.45, False, "NO_ACTION", 0.05, 0.20, False),
        ("repeated_failure", "Account blocked for online transactions", 200000, 500000, 3, 0.15, 0.35, False, "NO_ACTION", 0.02, 0.15, False),
        ("strong_history", "Insufficient balance on primary card", 50000, 350000, 1, 0.88, 0.99, False, "CREATE_PAYMENT_LINK", 0.80, 0.92, False),
        ("weak_history", "Do not honor - generic decline", 100000, 400000, 2, 0.25, 0.45, False, "SEND_NOTIFICATION", 0.35, 0.55, False),
        ("high_amount", "High value transaction step-up auth timeout", 5500000, 15000000, 1, 0.80, 0.95, False, "CREATE_PAYMENT_LINK", 0.75, 0.90, True),
        ("suspicious_velocity", "Velocity limit exceeded across multiple attempts", 300000, 1200000, 3, 0.40, 0.65, True, "ESCALATE_CASE", 0.20, 0.40, True),
        ("already_recovered", "Payment completed on alternate session", 150000, 450000, 0, 0.85, 0.95, False, "NO_ACTION", 0.0, 0.0, False),
        ("ambiguous", "Transaction declined by risk scoring filter", 120000, 600000, 1, 0.50, 0.70, False, "ESCALATE_CASE", 0.45, 0.65, True),
    ]

    cases = []
    case_num = 1
    random.seed(42)

    for i in range(120):
        scenario = scenarios[i % len(scenarios)]
        cat, reason, min_amt, max_amt, retries, min_score, max_score, vel, action, min_p, max_p, req_human = scenario

        amount = random.randint(min_amt, max_amt)
        score = round(random.uniform(min_score, max_score), 2)
        prob = round(random.uniform(min_p, max_p), 2)
        confidence = round(random.uniform(0.85, 0.98), 2)

        c = {
            "case_id": f"syn-case-{case_num:04d}",
            "scenario": cat,
            "payment": {
                "id": str(uuid.UUID(int=case_num)),
                "amount_minor": amount,
                "currency": "INR",
                "status": "recovered" if cat == "already_recovered" else "failed",
                "failure_reason": reason,
                "method": random.choice(["upi", "card", "netbanking"]),
            },
            "risk_signals": {
                "retry_count": retries,
                "customer_history_score": score,
                "velocity_flag": vel,
            },
            "ground_truth": {
                "recommended_action": action,
                "expected_probability": prob,
                "confidence": confidence,
                "requires_human": req_human,
                "expected_policy_decision": (
                    "DENY" if cat == "already_recovered" or retries > 3
                    else ("HUMAN_APPROVAL" if amount > 5000000 or vel or req_human else "ALLOW")
                )
            }
        }
        cases.append(c)
        case_num += 1

    return cases

if __name__ == "__main__":
    cases = generate_synthetic_cases()
    with open("data/synthetic/cases.json", "w") as f:
        json.dump(cases, f, indent=2)
    print(f"Generated {len(cases)} synthetic cases in data/synthetic/cases.json")
