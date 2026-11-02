import pandas as pd
import streamlit as st
from knowledge_base import initialize_knowledge_base

from database import (
    initialize_database,
    save_resource,
    get_all_resources,
    publish_resource,
)
from recommendations import recommend_pathways


# --------------------------------------------------
# APPLICATION INITIALIZATION
# --------------------------------------------------

st.set_page_config(
    page_title="Resourcera",
    page_icon="🌱",
    layout="wide",
)

initialize_database()
initialize_knowledge_base()


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("Resourcera")
st.subheader("Turning agricultural waste into valuable resources")

st.write(
    "Resourcera helps identify potential uses for agricultural "
    "residues and maintain records of available resources."
)

st.warning(
    "Prototype status: recommendations use predefined rules, "
    "not a trained AI model. Pathway suitability must be validated "
    "before commercial use."
)


# --------------------------------------------------
# RESOURCE REGISTRATION
# --------------------------------------------------

st.header("Register an agricultural resource")

with st.form("resource_form"):
    waste_type_selection = st.selectbox(
        "Type of agricultural waste",
        [
            "Cassava peels",
            "Cocoa pod husks",
            "Maize residues",
            "Rice husks",
            "Orange peels",
            "Other",
        ],
    )

    custom_waste_type = st.text_input(
        "If you selected Other, specify the waste type",
        placeholder=(
            "e.g. plantain peels, yam peels, sugarcane bagasse"
        ),
    )

    quantity_kg = st.number_input(
        "Available quantity (kg)",
        min_value=0.0,
        value=100.0,
        step=10.0,
    )

    location = st.text_input(
        "Location",
        placeholder="e.g. Akure, Ondo State",
    )

    condition = st.selectbox(
        "Material condition",
        [
            "Fresh or wet",
            "Partly dried",
            "Dry",
            "Unknown",
        ],
    )
    available_from = st.date_input(
        "When will this resource be available?",
        value=None,
        help="Leave blank if the availability date is not yet known.",
    )
    submitted = st.form_submit_button("Register and analyze")


# PROCESS SUBMISSION

if submitted:
    if (
        waste_type_selection == "Other"
        and not custom_waste_type.strip()
    ):
        st.error("Please specify the agricultural waste type.")

    elif quantity_kg <= 0:
        st.error("Enter a quantity greater than zero.")

    elif not location.strip():
        st.error("Enter the resource location.")

    else:
        if waste_type_selection == "Other":
            waste_type = custom_waste_type.strip()
        else:
            waste_type = waste_type_selection

        try:
            resource_id = save_resource(
                waste_type=waste_type,
                quantity_kg=quantity_kg,
                location=location.strip(),
                condition=condition,
                available_from=available_from,
            )

            st.success("Resource saved successfully.")

            st.write(f"**Resource ID:** `{resource_id}`")

            st.header("Resource profile")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Available quantity",
                f"{quantity_kg:,.1f} kg",
            )

            col2.write("**Material**")
            col2.write(waste_type)

            col3.write("**Location**")
            col3.write(location.strip())

            st.write(f"**Condition:** {condition}")

            st.header("Potential recovery pathways")

            results = recommend_pathways(
                waste_type,
                condition,
            )

            for index, item in enumerate(results, start=1):
                with st.expander(
                    f"{index}. {item['pathway']}",
                    expanded=True,
                ):
                    st.write("**Why this may be suitable**")
                    st.write(item["reason"])

                    st.write("**Important considerations**")
                    st.write(item["caution"])

            st.caption(
                "Recommendations are preliminary. "
                "No buyer, market price, profitability, or "
                "environmental benefit has been verified."
            )

        except (ValueError, OSError) as error:
            st.error(
                f"Could not save the resource: {error}"
            )


# --------------------------------------------------
# SAVED RESOURCE REGISTRY
# --------------------------------------------------

st.divider()

st.header("Agricultural Resource Registry")

st.write(
    "Browse resource records saved in the local database."
)

try:
    resources = get_all_resources()

    if resources:
        df = pd.DataFrame(resources)

        df = df.rename(
            columns={
                "resource_id": "Resource ID",
                "waste_type": "Waste Type",
                "quantity_kg": "Quantity (kg)",
                "location": "Location",
                "condition": "Condition",
                "registered_at": "Date Registered (UTC)",
                "available_from": "Available From",
            }
        )

        st.metric(
            "Total registered resources",
            len(resources),
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )
        st.subheader("Manage Resource Publication")

        resource_options = {
            (
                f'{resource["waste_type"]} — '
                f'{resource["quantity_kg"]:,.1f} kg — '
                f'{resource["location"]} — '
                f'ID: {resource["resource_id"][:8]}'
            ): resource["resource_id"]
            for resource in resources
        }

        selected_label = st.selectbox(
            "Select a resource",
            list(resource_options.keys()),
        )
        available_from = st.date_input(
            "When will this resource be available?",
            value=None,
            help="Leave blank if the availability date is not yet known.",
        )
        selected_resource_id = resource_options[selected_label]

        selected_resource = next(
            resource
            for resource in resources
            if resource["resource_id"] == selected_resource_id
        )

        is_published = bool(selected_resource["is_published"])

        st.write(
            "Current status:",
            "Published publicly" if is_published else "Private",
        )

        if is_published:
            if st.button(
                "Unpublish resource",
                key="unpublish_resource",
            ):
                if publish_resource(
                    selected_resource_id,
                    published=False,
                ):
                    st.success("Resource unpublished successfully.")
                    st.rerun()
                else:
                    st.error("Resource could not be unpublished.")
        else:
            if st.button(
                "Publish resource",
                key="publish_resource",
            ):
                if publish_resource(
                    selected_resource_id,
                    published=True,
                ):
                    st.success("Resource published successfully.")
                    st.rerun()
                else:
                    st.error("Resource could not be published.")
    else:
        st.info(
            "No resources registered yet. "
            "Submit a resource using the form above."
        )

except (OSError, pd.errors.DatabaseError) as error:
    st.error(
        f"Could not load the resource registry: {error}"
    )