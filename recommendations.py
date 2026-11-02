
def recommend_pathways(waste_type, condition):
    """Return preliminary resource-use options based on simple rules."""

    pathways = {
        "Cassava peels": [
            {
                "pathway": "Animal feed processing",
                "reason": (
                    "Cassava peels may be usable as feed after "
                    "appropriate processing and safety checks."
                ),
                "caution": (
                    "Do not feed untreated material without assessing "
                    "cyanide risk, spoilage, and animal-feed suitability."
                ),
            },
            {
                "pathway": "Composting",
                "reason": (
                    "Organic cassava residues may be suitable for "
                    "managed composting."
                ),
                "caution": "Manage moisture, aeration, and decomposition.",
            },
        ],
        "Cocoa pod husks": [
            {
                "pathway": "Composting",
                "reason": (
                    "Cocoa pod husks can be assessed as a feedstock "
                    "for organic compost."
                ),
                "caution": (
                    "Assess contamination, decomposition, and soil-use "
                    "requirements."
                ),
            },
            {
                "pathway": "Biochar research",
                "reason": (
                    "Dry cocoa pod husks may be investigated as "
                    "a feedstock for controlled thermal conversion."
                ),
                "caution": (
                    "Requires suitable equipment, emission controls, "
                    "and process validation."
                ),
            },
        ],
        "Maize residues": [
            {
                "pathway": "Composting",
                "reason": (
                    "Plant residues can contribute carbon to a "
                    "managed composting process."
                ),
                "caution": "Balance carbon-rich material with suitable nitrogen sources.",
            },
            {
                "pathway": "Briquette feasibility assessment",
                "reason": (
                    "Dry residues may be evaluated for solid-fuel "
                    "briquette production."
                ),
                "caution": (
                    "Test moisture, binding requirements, combustion "
                    "performance, and emissions."
                ),
            },
        ],
        "Rice husks": [
            {
                "pathway": "Controlled thermal processing research",
                "reason": (
                    "Rice husks may be assessed for applications "
                    "involving their silica-rich ash."
                ),
                "caution": (
                    "Requires controlled processing and validation "
                    "of the intended end product."
                ),
            },
            {
                "pathway": "Briquette feasibility assessment",
                "reason": (
                    "Rice husks may be evaluated for suitable "
                    "solid-fuel applications."
                ),
                "caution": "Test combustion properties and emissions.",
            },
        ],
        "Orange peels": [
            {
                "pathway": "Composting",
                "reason": (
                    "Orange peels may be suitable for managed "
                    "organic-waste composting."
                ),
                "caution": (
                    "Manage acidity, moisture, and the balance "
                    "of materials in the compost."
                ),
            },
            {
                "pathway": "Biogas feasibility assessment",
                "reason": (
                    "Wet citrus residues may be assessed for "
                    "anaerobic digestion."
                ),
                "caution": (
                    "Citrus oils and acidity can inhibit digestion; "
                    "test the feedstock and process conditions."
                ),
            },
        ],
    }

    results = pathways.get(waste_type, [])

    if not results:
        return [
            {
                "pathway": "Feedstock assessment required",
                "reason": (
                    "There is not enough information to recommend "
                    "a specific pathway for this material."
                ),
                "caution": (
                    "Identify the material and assess its composition, "
                    "contamination, moisture, and local requirements."
                ),
            }
        ]

    if condition == "Unknown":
        return [
            {
                **item,
                "caution": (
                    item["caution"]
                    + " Material condition is unknown; assess it before proceeding."
                ),
            }
            for item in results
        ]

    return results
    