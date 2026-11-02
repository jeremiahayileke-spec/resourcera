
import sys
import streamlit as st
import google

st.write("Python interpreter:", sys.executable)
st.write("Google package location:", list(google.__path__))
st.set_page_config(page_title="Resourcera AI Engine Test")

st.title("Resourcera — AI Resource Intelligence")

st.write("Test material: Rice Husks")

if st.button("Run AI Assessment"):
    try:
        with st.spinner("Gemini is assessing the registered pathways..."):
            from ai_engine import assess_resource_with_ai
            result = assess_resource_with_ai(
                material_name="Rice Husks",
                quantity_kg=1000,
                condition="Dry",
                location="Akure, Ondo State, Nigeria",
            )

        if result["status"] == "success":
            assessment = result["assessment"]
            st.subheader("Raw AI Response — Validation")
            st.json(assessment)

            st.success("AI assessment completed.")

            st.subheader("Overall Assessment")
            st.write(assessment["overall_assessment"])

            st.subheader("Candidate Pathways")

            for item in assessment["pathway_assessments"]:
                with st.expander(item["pathway_name"], expanded=True):
                    st.markdown(f"**Output:** {item['output_product']}")
                    st.markdown(
                        f"**Preliminary relevance:** "
                        f"{item['preliminary_relevance']}"
                    )
                    st.markdown("**Reasoning**")
                    st.write(item["reasoning"])
                    st.markdown(
                        f"**Verification status:** "
                        f"{item['verification_status']}"
                    )
                    st.markdown("**Missing information**")
                    for missing in item["missing_information"]:
                        st.markdown(f"- {missing}")

            st.subheader("Important Limitations")
            for limitation in assessment["important_limitations"]:
                st.write(f"- {limitation}")
        else:
            st.warning(result["message"])

    except Exception as error:
        st.error(f"{type(error).__name__}: {error}")
