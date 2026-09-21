from pydantic import BaseModel


class FinancialInputs(BaseModel):
    """Variables the LLM extracts from natural language; math is done in Python."""

    price: float = 0.0
    units_sold: float = 0.0
    unit_variable_cost: float = 0.0
    fixed_costs: float = 0.0
    marketing_spend: float = 0.0
    new_customers: float = 0.0
    avg_revenue_per_customer_month: float = 0.0
    gross_margin_pct: float = 0.0
    monthly_churn_rate: float = 0.0
    monthly_revenue: float = 0.0
    monthly_expenses: float = 0.0
    cash_balance: float = 0.0
