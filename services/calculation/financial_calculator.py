class FinancialCalculator:
    """Deterministic financial formulas. Division by zero yields None, not a guess."""

    @staticmethod
    def revenue(price: float, units: float) -> float:
        return price * units

    @staticmethod
    def gross_profit(revenue: float, cogs: float) -> float:
        return revenue - cogs

    @staticmethod
    def cac(marketing_spend: float, new_customers: float) -> float | None:
        return marketing_spend / new_customers if new_customers > 0 else None

    @staticmethod
    def ltv(
        avg_revenue_per_customer_month: float, gross_margin_pct: float, monthly_churn_rate: float
    ) -> float | None:
        """gross_margin_pct is a fraction (0.7 = 70%)."""
        if monthly_churn_rate <= 0:
            return None
        return avg_revenue_per_customer_month * gross_margin_pct / monthly_churn_rate

    @staticmethod
    def break_even_units(
        fixed_costs: float, price: float, unit_variable_cost: float
    ) -> float | None:
        margin = price - unit_variable_cost
        return fixed_costs / margin if margin > 0 else None

    @staticmethod
    def monthly_burn(monthly_revenue: float, monthly_expenses: float) -> float:
        return max(monthly_expenses - monthly_revenue, 0.0)

    @staticmethod
    def runway_months(cash_balance: float, monthly_burn: float) -> float | None:
        return cash_balance / monthly_burn if monthly_burn > 0 else None
