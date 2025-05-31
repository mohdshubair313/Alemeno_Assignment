# core/helpers.py

def calculate_approved_limit(monthly_income: float) -> float:
    """
    Approves 36x of monthly salary, rounded to nearest lakh.
    """
    return round((36 * monthly_income) / 100000) * 100000
