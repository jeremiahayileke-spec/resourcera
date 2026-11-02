from datetime import date


def match_resources(
    resources,
    required_waste_type,
    minimum_quantity_kg,
    acceptable_conditions=None,
    needed_by=None,
):
    """
    Match published resources against a buyer's requirements.

    Returns potential matches with transparent reasons.
    This does not confirm quality, availability, or a transaction.
    """

    if minimum_quantity_kg <= 0:
        raise ValueError("Minimum quantity must be greater than zero.")

    if not required_waste_type.strip():
        raise ValueError("Required waste type cannot be empty.")

    if needed_by is not None and not isinstance(needed_by, date):
        raise ValueError("needed_by must be a date or None.")

    acceptable_conditions = acceptable_conditions or [
        "Fresh or wet",
        "Partly dried",
        "Dry",
        "Unknown",
    ]

    matches = []

    for resource in resources:
        reasons = []
        issues = []

        # 1. Material type
        if (
            resource["waste_type"].strip().casefold()
            != required_waste_type.strip().casefold()
        ):
            continue

        reasons.append("Material type matches.")

        # 2. Quantity
        quantity = float(resource["quantity_kg"])

        if quantity < minimum_quantity_kg:
            continue

        reasons.append(
            f"Quantity meets the requirement "
            f"({quantity:,.1f} kg available)."
        )

        # 3. Condition
        condition = resource["condition"]

        if condition not in acceptable_conditions:
            continue

        if condition == "Unknown":
            issues.append("Material condition has not been assessed.")
        else:
            reasons.append(f"Condition is listed as {condition}.")

        # 4. Availability date
        available_from = resource.get("available_from")

        if available_from:
            availability_date = date.fromisoformat(available_from)

            if needed_by and availability_date > needed_by:
                continue

            reasons.append(
                f"Supplier-listed availability date: {available_from}."
            )
        else:
            issues.append("Availability date has not been provided.")

        matches.append(
            {
                "resource_id": resource["resource_id"],
                "waste_type": resource["waste_type"],
                "quantity_kg": quantity,
                "location": resource["location"],
                "condition": condition,
                "available_from": available_from,
                "match_reasons": reasons,
                "issues": issues,
                "match_status": "Potential match — verification required",
            }
        )

    # Larger quantities first; this is not a profitability ranking.
    matches.sort(
        key=lambda item: item["quantity_kg"],
        reverse=True,
    )

    return matches
def match_supplier_combinations(
    resources,
    required_waste_type,
    minimum_quantity_kg,
    acceptable_conditions=None,
    needed_by=None,
):
    from datetime import date

    acceptable_conditions = acceptable_conditions or [
        "Fresh or wet", "Partly dried", "Dry", "Unknown"
    ]

    eligible = []

    for resource in resources:
        if resource["waste_type"].strip().casefold() != required_waste_type.strip().casefold():
            continue

        if resource["condition"] not in acceptable_conditions:
            continue

        available_from = resource.get("available_from")

        if available_from and needed_by:
            if date.fromisoformat(available_from) > needed_by:
                continue

        eligible.append(resource)

    # Never combine suppliers from different towns.
    towns = {}

    for resource in eligible:
        town = " ".join(resource["location"].strip().casefold().split())
        towns.setdefault(town, []).append(resource)

    results = []

    for town, suppliers in towns.items():
        suppliers.sort(
            key=lambda item: float(item["quantity_kg"]),
            reverse=True,
        )

        selected = []
        total = 0

        for supplier in suppliers:
            selected.append(supplier)
            total += float(supplier["quantity_kg"])

            if total >= minimum_quantity_kg:
                results.append({
                    "town": town.title(),
                    "suppliers": selected,
                    "total_quantity_kg": total,
                    "excess_quantity_kg": total - minimum_quantity_kg,
                })
                break

    return results