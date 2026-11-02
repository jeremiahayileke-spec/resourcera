import pytest
from economics import estimate_aggregation_cost


def test_calculates_total_aggregation_cost():
    result = estimate_aggregation_cost(
        total_quantity_kg=1000,
        transport_cost=20000,
        processing_cost_per_kg=15,
        acquisition_cost_per_kg=5,
    )

    assert result["total_cost"] == 40000
    assert result["cost_per_kg"] == 40


def test_rejects_zero_quantity():
    with pytest.raises(ValueError):
        estimate_aggregation_cost(
            total_quantity_kg=0,
            transport_cost=20000,
            processing_cost_per_kg=15,
        )


def test_rejects_negative_cost():
    with pytest.raises(ValueError):
        estimate_aggregation_cost(
            total_quantity_kg=1000,
            transport_cost=-20000,
            processing_cost_per_kg=15,
        )

from economics import assess_processing_opportunity


def test_positive_processing_opportunity():
    result = assess_processing_opportunity(
        total_cost=40000,
        output_quantity_kg=700,
        selling_price_per_kg=100,
    )

    assert result["revenue"] == 70000
    assert result["gross_profit"] == 30000
    assert result["gross_margin_percent"] == pytest.approx(42.857, abs=0.001)
    assert result["assessment"] == "Positive gross margin"


def test_negative_processing_opportunity():
    result = assess_processing_opportunity(
        total_cost=50000,
        output_quantity_kg=700,
        selling_price_per_kg=50,
    )

    assert result["gross_profit"] == -15000
    assert result["assessment"] == "Negative gross margin"


def test_rejects_invalid_output_quantity():
    with pytest.raises(ValueError):
        assess_processing_opportunity(
            total_cost=40000,
            output_quantity_kg=0,
            selling_price_per_kg=100,
        )