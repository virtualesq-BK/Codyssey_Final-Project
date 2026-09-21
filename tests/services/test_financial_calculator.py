import pytest

from services.calculation.financial_calculator import FinancialCalculator as F


def test_revenue_and_gross_profit():
    assert F.revenue(100, 50) == 5000
    assert F.gross_profit(5000, 2000) == 3000


def test_cac_ltv():
    assert F.cac(1000, 10) == 100
    assert F.cac(1000, 0) is None
    assert F.ltv(100, 0.5, 0.1) == pytest.approx(500)
    assert F.ltv(100, 0.5, 0) is None


def test_break_even():
    assert F.break_even_units(1000, 20, 10) == 100
    assert F.break_even_units(1000, 10, 10) is None


def test_burn_and_runway():
    assert F.monthly_burn(300, 1000) == 700
    assert F.monthly_burn(1500, 1000) == 0
    assert F.runway_months(7000, 700) == 10
    assert F.runway_months(7000, 0) is None
