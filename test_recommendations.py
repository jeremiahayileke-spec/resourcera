
from recommendations import recommend_pathways


def test_cocoa_husks_have_preliminary_options():
    results = recommend_pathways("Cocoa pod husks", "Partly dried")

    assert len(results) > 0
    assert all("pathway" in item for item in results)
    assert all("reason" in item for item in results)
    assert all("caution" in item for item in results)


def test_unknown_waste_does_not_get_a_specific_recommendation():
    results = recommend_pathways("Other", "Unknown")

    assert len(results) == 1
    assert results[0]["pathway"] == "Feedstock assessment required"


def test_unknown_condition_adds_a_caution():
    results = recommend_pathways("Orange peels", "Unknown")

    assert all("condition is unknown" in item["caution"] for item in results)
