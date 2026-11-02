
import streamlit as st
from google import genai

st.set_page_config(page_title="Resourcera Gemini Test")

st.title("Resourcera — Gemini Connection Test")

if st.button("Test Gemini Connection"):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Reply with exactly: Resourcera Gemini connection successful."
        )

        if response.text:
            st.success("Gemini connection successful.")
            st.write(response.text)
        else:
            st.error("Gemini returned an empty response.")

        client.close()

    except Exception as error:
        st.error(f"Connection test failed: {type(error).__name__}")
        st.code(str(error))
