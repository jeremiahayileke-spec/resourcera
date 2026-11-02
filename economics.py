def estimate_aggregation_cost(
    total_quantity_kg,
    transport_cost,
    processing_cost_per_kg,
    acquisition_cost_per_kg=0,
):
    if total_quantity_kg <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if min(
        transport_cost,
        processing_cost_per_kg,
        acquisition_cost_per_kg,
    ) < 0:
        raise ValueError("Costs cannot be negative.")

    total_transport_cost = transport_cost
    total_processing_cost = (
        total_quantity_kg * processing_cost_per_kg
    )
    total_acquisition_cost = (
        total_quantity_kg * acquisition_cost_per_kg
    )

    total_cost = (
        total_transport_cost
        + total_processing_cost
        + total_acquisition_cost
    )

    return {
        "quantity_kg": total_quantity_kg,
        "transport_cost": total_transport_cost,
        "processing_cost": total_processing_cost,
        "acquisition_cost": total_acquisition_cost,
        "total_cost": total_cost,
        "cost_per_kg": total_cost / total_quantity_kg,
    }
def calculate_break_even_price(
    total_cost,
    output_quantity_kg,
):
    if total_cost < 0:
        raise ValueError("Total cost cannot be negative.")

    if output_quantity_kg <= 0:
        raise ValueError("Output quantity must be greater than zero.")

    return total_cost / output_quantity_kg

def calculate_break_even_price(
    total_cost,
    output_quantity_kg,
):
    if total_cost < 0:
        raise ValueError("Total cost cannot be negative.")

    if output_quantity_kg <= 0:
        raise ValueError("Output quantity must be greater than zero.")

    return total_cost / output_quantity_kg

def assess_processing_opportunity(
    total_cost,
    output_quantity_kg,
    selling_price_per_kg,
):
    if total_cost < 0:
        raise ValueError("Total cost cannot be negative.")

    if output_quantity_kg <= 0:
        raise ValueError("Output quantity must be greater than zero.")

    if selling_price_per_kg < 0:
        raise ValueError("Selling price cannot be negative.")

    revenue = output_quantity_kg * selling_price_per_kg
    gross_profit = revenue - total_cost

    gross_margin = (
        (gross_profit / revenue) * 100
        if revenue > 0 else 0
    )

    break_even_price = total_cost / output_quantity_kg

    return {
        "revenue": revenue,
        "total_cost": total_cost,
        "gross_profit": gross_profit,
        "gross_margin_percent": gross_margin,
        "break_even_price": break_even_price,
        "assessment": (
            "Positive gross margin"
            if gross_profit > 0
            else "Break-even"
            if gross_profit == 0
            else "Negative gross margin"
        ),
    }