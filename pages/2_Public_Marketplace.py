import streamlit as st

from database import initialize_database, get_public_resources
from knowledge_base import get_material_opportunities
from matching import match_resources, match_supplier_combinations
from recommendations import recommend_pathways
from economics import (
    estimate_aggregation_cost,
    calculate_break_even_price,
    assess_processing_opportunity,
)
from ai_engine import assess_resource_with_ai

initialize_database()

st.set_page_config(
    page_title="Resourcera Marketplace",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 Resourcera Public Marketplace")
st.write(
    "Discover agricultural resources made available "
    "by suppliers for potential reuse and processing."
)

all_resources = get_public_resources()
resources = all_resources

st.divider()
st.header("🔎 Find Resources for Your Needs")

st.write(
    "Describe the agricultural material you need. "
    "Resourcera will identify potential matches from published listings."
)

if resources:
    with st.form("resource_matching_form"):
        required_waste_type = st.selectbox(
            "What material do you need?",
            sorted({
                resource["waste_type"]
                for resource in resources
            }),
        )

        minimum_quantity_kg = st.number_input(
            "Minimum quantity required (kg)",
            min_value=1.0,
            value=100.0,
            step=50.0,
        )

        acceptable_conditions = st.multiselect(
            "Acceptable material conditions",
            [
                "Fresh or wet",
                "Partly dried",
                "Dry",
                "Unknown",
            ],
            default=["Dry", "Partly dried"],
        )

        needed_by = st.date_input(
            "Latest acceptable availability date (optional)",
            value=None,
        )

        find_matches = st.form_submit_button(
            "Find Potential Matches"
        )

    if find_matches:
        if not acceptable_conditions:
            st.warning("Select at least one acceptable condition.")
        else:
            try:
                matches = match_resources(
                    resources=resources,
                    required_waste_type=required_waste_type,
                    minimum_quantity_kg=minimum_quantity_kg,
                    acceptable_conditions=acceptable_conditions,
                    needed_by=needed_by,
                )

                if matches:
                    st.subheader(
                        f"{len(matches)} Potential Match(es)"
                    )

                    for match in matches:
                        with st.container(border=True):
                            st.subheader(match["waste_type"])

                            st.write(
                                f'**Quantity:** '
                                f'{match["quantity_kg"]:,.1f} kg'
                            )
                            st.write(
                                f'**Location:** {match["location"]}'
                            )
                            st.write(
                                f'**Condition:** {match["condition"]}'
                            )

                            if match["available_from"]:
                                st.write(
                                    f'**Listed availability:** '
                                    f'{match["available_from"]}'
                                )
                            else:
                                st.warning(
                                    "Availability date has not been provided."
                                )

                            st.write("**Why it matched**")
                            for reason in match["match_reasons"]:
                                st.write(f"- {reason}")

                            for issue in match["issues"]:
                                st.warning(issue)

                            st.info(match["match_status"])

                else:
                    st.info(
                        "No resources currently meet all the "
                        "selected matching criteria."
                    )

            except (ValueError, TypeError) as error:
                st.error(f"Could not complete matching: {error}")
else:
    st.info(
        "Matching will become available when suppliers publish resources."
    )

st.divider()

if resources:
    st.subheader("Find Agricultural Resources")

    search_query = st.text_input(
        "Search by waste type or location",
        placeholder="e.g. cocoa, cassava, Akure",
    )

    available_locations = sorted(
        {
            resource["location"]
            for resource in resources
            if resource["location"]
        }
    )

    selected_location = st.selectbox(
        "Filter by location",
        ["All locations"] + available_locations,
    )

    min_quantity = st.number_input(
        "Minimum available quantity (kg)",
        min_value=0.0,
        value=0.0,
        step=10.0,
    )

    filtered_resources = []

    for resource in all_resources:
        matches_search = (
            search_query.strip().lower() in
            (
                resource["waste_type"] + " " +
                resource["location"]
            ).lower()
        )

        matches_location = (
            selected_location == "All locations"
            or resource["location"] == selected_location
        )

        matches_quantity = (
            resource["quantity_kg"] >= min_quantity
        )

        if (
            matches_search
            and matches_location
            and matches_quantity
        ):
            filtered_resources.append(resource)

    resources = filtered_resources

    st.caption(
        f"{len(resources)} resource(s) match your filters."
    )

if not all_resources:
    st.info(
        "No resources have been published yet. "
        "Check back later."
    )

elif not resources:
    st.info(
        "No published resources match your current filters. "
        "Try changing your search criteria."
    )

else:
    st.subheader(f"{len(resources)} Published Resources")

    for resource in resources:
        with st.container(border=True):
            st.subheader(resource["waste_type"])

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Available quantity",
                f'{resource["quantity_kg"]:,.1f} kg'
            )

            col2.write("**Location**")
            col2.write(resource["location"])

            col3.write("**Condition**")
            col3.write(resource["condition"])

            st.write("**Potential transformation pathways**")

            pathways = recommend_pathways(
                resource["waste_type"],
                resource["condition"],
            )

            for pathway in pathways:
                st.markdown(
                    f'**{pathway["pathway"]}**'
                )
                st.write(pathway["reason"])

                if pathway.get("caution"):
                    st.warning(pathway["caution"])

            st.divider()
            st.write("**Knowledge Base Processing Opportunities**")

            opportunities = get_material_opportunities(
                resource["waste_type"]
            )

            if opportunities:
                for opportunity in opportunities:
                    st.write(
                        f"- {opportunity['pathway_name']} → "
                        f"{opportunity['output_product']}"
                    )

                    st.caption(
                        f"Evidence status: "
                        f"{opportunity['verification_status']}"
                    )
            else:
                st.info(
                    "No processing opportunities are currently "
                    "registered for this material."
                )

            st.divider()
            st.write("### 🤖 AI Resource Intelligence")

            if st.button(
                "Assess this resource with Gemini",
                key=f"ai_assess_{resource['resource_id']}",
            ):
                try:
                    with st.spinner(
                        "Gemini is assessing this resource..."
                    ):
                        ai_result = assess_resource_with_ai(
                            material_name=resource["waste_type"],
                            quantity_kg=resource["quantity_kg"],
                            condition=resource["condition"],
                            location=resource["location"],
                        )

                    if ai_result["status"] == "success":
                        assessment = ai_result["assessment"]

                        st.success("AI assessment completed.")
                        st.write(assessment["overall_assessment"])

                        for item in assessment["pathway_assessments"]:
                            with st.expander(
                                item["pathway_name"],
                                expanded=True,
                            ):
                                st.write(
                                    "**Output:**",
                                    item["output_product"],
                                )
                                st.write(
                                    "**Preliminary relevance:**",
                                    item["preliminary_relevance"],
                                )
                                st.write("**Reasoning:**")
                                st.write(item["reasoning"])
                                st.write(
                                    "**Verification:**",
                                    item["verification_status"],
                                )
                                st.write("**Missing information:**")

                                for missing in item["missing_information"]:
                                    st.write(f"- {missing}")

                        st.write("**Important limitations**")

                        for limitation in assessment["important_limitations"]:
                            st.write(f"- {limitation}")

                        st.caption(
                            "AI-generated preliminary assessment. "
                            "Not a technical certification or proof "
                            "of commercial viability."
                        )

                    else:
                        st.warning(ai_result["message"])

                except Exception as error:
                    st.error(
                        f"AI assessment failed: "
                        f"{type(error).__name__}: {error}"
                    )

st.divider()
st.header("📦 Combine Suppliers in the Same Town")

if all_resources:
    if st.button("Find Combined Supplier Matches"):
        combinations = match_supplier_combinations(
            resources=all_resources,
            required_waste_type=required_waste_type,
            minimum_quantity_kg=minimum_quantity_kg,
            acceptable_conditions=acceptable_conditions,
            needed_by=needed_by,
        )

        if combinations:
            for combination in combinations:
                st.subheader(f"Town: {combination['town']}")

                st.write(
                    f"**Combined quantity:** "
                    f"{combination['total_quantity_kg']:,.1f} kg"
                )

                st.write(
                    f"**Excess quantity:** "
                    f"{combination['excess_quantity_kg']:,.1f} kg"
                )

                for supplier in combination["suppliers"]:
                    st.write(
                        f"- {supplier['quantity_kg']:,.1f} kg "
                        f"from {supplier['location']} "
                        f"({supplier['condition']})"
                    )
        else:
            st.info(
                "No same-town supplier combination meets this requirement."
            )

st.divider()
st.header("💰 Estimate Aggregation Costs")

st.write(
    "Estimate the cost of collecting and processing "
    "agricultural resources."
)

with st.form("aggregation_cost_form"):
    quantity = st.number_input(
        "Total quantity (kg)",
        min_value=1.0,
        value=1000.0,
    )

    transport = st.number_input(
        "Total transport cost (₦)",
        min_value=0.0,
        value=20000.0,
    )

    processing = st.number_input(
        "Processing cost per kg (₦)",
        min_value=0.0,
        value=15.0,
    )

    acquisition = st.number_input(
        "Acquisition cost per kg (₦)",
        min_value=0.0,
        value=5.0,
    )

    calculate = st.form_submit_button("Calculate Estimated Cost")

if calculate:
    result = estimate_aggregation_cost(
        total_quantity_kg=quantity,
        transport_cost=transport,
        processing_cost_per_kg=processing,
        acquisition_cost_per_kg=acquisition,
    )

    st.metric(
        "Total Estimated Cost",
        f"₦{result['total_cost']:,.2f}",
    )

    st.metric(
        "Estimated Cost per KG",
        f"₦{result['cost_per_kg']:,.2f}",
    )

st.divider()
st.header("Break-Even Price Calculator")

with st.form("break_even_form"):
    total_cost = st.number_input(
        "Total production cost (₦)",
        min_value=0.0,
        value=40000.0,
    )

    output_quantity = st.number_input(
        "Expected finished product quantity (kg)",
        min_value=0.1,
        value=700.0,
    )

    calculate = st.form_submit_button("Calculate Break-Even Price")

if calculate:
    break_even = calculate_break_even_price(
        total_cost=total_cost,
        output_quantity_kg=output_quantity,
    )

    st.metric("Break-Even Price", f"₦{break_even:,.2f}/kg")

st.divider()
st.header("Processing Opportunity Assessment")

st.write(
    "Evaluate the economics of converting agricultural "
    "waste into a marketable product."
)

with st.form("opportunity_assessment"):
    total_cost = st.number_input(
        "Total production cost (₦)",
        min_value=0.0,
        value=40000.0,
    )

    output_quantity = st.number_input(
        "Expected finished product (kg)",
        min_value=0.1,
        value=700.0,
    )

    selling_price = st.number_input(
        "Actual buyer quotation per kg (₦)",
        min_value=0.0,
        value=100.0,
    )

    assess = st.form_submit_button(
        "Assess Processing Opportunity"
    )

if assess:
    result = assess_processing_opportunity(
        total_cost=total_cost,
        output_quantity_kg=output_quantity,
        selling_price_per_kg=selling_price,
    )

    st.subheader("Assessment Results")

    st.metric("Expected Revenue", f"₦{result['revenue']:,.2f}")
    st.metric("Total Production Cost", f"₦{result['total_cost']:,.2f}")
    st.metric("Estimated Gross Profit", f"₦{result['gross_profit']:,.2f}")
    st.metric("Gross Margin", f"{result['gross_margin_percent']:.2f}%")
    st.metric("Break-Even Price", f"₦{result['break_even_price']:,.2f}/kg")

    st.info(result["assessment"])

    st.caption(
        "Preliminary assessment only. Gross profit excludes "
        "any costs not included in the production-cost input. "
        "Buyer quotations must be independently verified."
    )