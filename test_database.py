import pytest
import database
import database

@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_resourcera.db"

    monkeypatch.setattr(database, "DATABASE_PATH", test_db_path)

    database.initialize_database()

    return test_db_path

def test_new_resource_is_private_by_default(temporary_database):
    resource_id = database.save_resource(
        "Cocoa pod husks",
        250,
        "Akure, Ondo State",
        "Partly dried",
    )

    resources = database.get_all_resources()
    resource = next(
        item for item in resources
        if item["resource_id"] == resource_id
    )

    assert resource["is_published"] == 0
    assert database.get_public_resources() == []


def test_published_resource_appears_in_public_results(
    temporary_database,
):
    resource_id = database.save_resource(
        "Cocoa pod husks",
        250,
        "Akure, Ondo State",
        "Partly dried",
    )

    assert database.publish_resource(resource_id) is True

    public_resources = database.get_public_resources()

    assert len(public_resources) == 1
    assert public_resources[0]["resource_id"] == resource_id
    assert public_resources[0]["waste_type"] == "Cocoa pod husks"


def test_unpublishing_removes_resource_from_public_results(
    temporary_database,
):
    resource_id = database.save_resource(
        "Rice husks",
        100,
        "Akure, Ondo State",
        "Dry",
    )

    database.publish_resource(resource_id)
    assert len(database.get_public_resources()) == 1

    assert database.publish_resource(
        resource_id,
        published=False,
    ) is True

    assert database.get_public_resources() == []


def test_unknown_resource_cannot_be_published(temporary_database):
    assert database.publish_resource("nonexistent-id") is False
    assert database.get_public_resources() == []
