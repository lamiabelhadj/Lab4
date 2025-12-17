def calculate_monthly_payment(amount: float, duration: int, annual_rate: float = 0.05):
    """
    Calcul du paiement mensuel pour un prêt (formule amortissement)
    """
    r = annual_rate / 12  # taux mensuel
    if r == 0:
        return amount / duration
    return amount * r / (1 - (1 + r) ** -duration)

def generate_amortization_schedule(amount: float, duration: int, annual_rate: float = 0.05):
    """
    Retourne la liste des paiements mensuels
    """
    monthly_payment = calculate_monthly_payment(amount, duration, annual_rate)
    schedule = []
    remaining = amount
    r = annual_rate / 12

    for i in range(1, duration + 1):
        interest = remaining * r
        principal = monthly_payment - interest
        remaining -= principal
        schedule.append({
            "month": i,
            "payment": round(monthly_payment, 2),
            "principal": round(principal, 2),
            "interest": round(interest, 2),
            "remaining": round(max(remaining, 0), 2)
        })
    return schedule
