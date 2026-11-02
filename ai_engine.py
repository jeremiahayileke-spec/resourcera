
import json
import streamlit as st
from google import genai

from knowledge_base import get_material_opportunities


def assess_resource_with_ai(
    material_name,
    quantity_kg,
    condition,
    location,
):
    """
    Uses Gemini to assess processing pathways retrieved
    from Resourcera's local knowledge base.
    """

    opportunities = get_material_opportunities(material_name)

    if not opportunities:
        return {
            "status": "no_data",
            "message": (
                "No candidate processing pathways are registered "
                "for this material in Resourcera's knowledge base."
            ),
        }

    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    knowledge_context = json.dumps(
        opportunities,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are Resourcera's agricultural resource intelligence assistant.

Your task is to assess candidate processing pathways for an
agricultural residue using ONLY the supplied knowledge base
as the source of registered pathway information.

RESOURCE DETAILS:
Material: {material_name}
Quantity: {quantity_kg} kg
Condition: {condition}
Location: {location}

REGISTERED KNOWLEDGE BASE:
{knowledge_context}

INSTRUCTIONS:

1. Assess each registered pathway separately.
2. Explain potential relevance using the supplied descriptions
   and relationship information.
3. Consider quantity, condition and location, but do not invent
   technical requirements or local market information.
4. Identify information that is missing before a real processing
   decision can be made.
5. Do not claim that a pathway is technically proven, profitable,
   safe or commercially viable.
6. Respect every verification_status value. An Unverified
   pathway must remain explicitly identified as unverified.
7. Do not invent prices, conversion yields, equipment costs,
   emissions reductions or buyer demand.
8. Rank pathways only as preliminary candidates, not certified
   recommendations.

Return valid JSON with this exact structure:

{{
  "overall_assessment": "Short assessment",
  "important_limitations": [
    "Limitation 1"
  ],
  "pathway_assessments": [
    {{
      "pathway_name": "Registered pathway name",
      "output_product": "Registered output product",
      "preliminary_relevance": "High, Medium, or Low",
      "reasoning": "Evidence-grounded explanation",
      "missing_information": [
        "Information needed"
      ],
      "verification_status": "Use the supplied status"
    }}
  ]
}}

Return JSON only. Do not include Markdown code fences.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        result = json.loads(response.text)

        if not isinstance(result, dict):
            raise ValueError("Gemini returned an invalid response structure.")

        if not isinstance(result.get("pathway_assessments"), list):
            raise ValueError("Missing pathway assessments.")

        
        registered = {
            item["pathway_name"]: item
            for item in opportunities
        }

        assessments = result["pathway_assessments"]

        if len(assessments) != len(registered):
            raise ValueError(
                "Gemini did not assess every registered pathway."
            )

        returned_names = []

        for assessment in assessments:

            name = assessment.get("pathway_name")

            if name not in registered:
                raise ValueError(
                    f"Unregistered pathway returned: {name}"
                )

            returned_names.append(name)

            required_fields = [
                "output_product",
                "preliminary_relevance",
                "reasoning",
                "missing_information",
                "verification_status",
            ]

            for field in required_fields:
                if not assessment.get(field):
                    raise ValueError(
                        f"Missing field '{field}' for {name}."
                    )

            if assessment["preliminary_relevance"] not in [
                "High", "Medium", "Low"
            ]:
                raise ValueError(
                    f"Invalid relevance rating for {name}."
                )

            if not isinstance(
                assessment["missing_information"], list
            ):
                raise ValueError(
                    f"Missing information must be a list for {name}."
                )

            source = registered[name]

            if assessment["output_product"] != source["output_product"]:
                raise ValueError(
                    f"Output product mismatch for {name}."
                )

            if (
                assessment["verification_status"]
                != source["verification_status"]
            ):
                raise ValueError(
                    f"Verification status mismatch for {name}."
                )

        if len(set(returned_names)) != len(registered):
            raise ValueError(
                "Gemini returned duplicate pathway assessments."
            )

        return {
            "status": "success",
            "assessment": result,
        }

    finally:
        client.close()
