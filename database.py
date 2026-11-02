
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone, date

DATABASE_PATH = Path(__file__).resolve().parent / "resourcera.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                resource_id TEXT PRIMARY KEY,
                waste_type TEXT NOT NULL,
                quantity_kg REAL NOT NULL CHECK (quantity_kg > 0),
                location TEXT NOT NULL,
                condition TEXT NOT NULL,
                registered_at TEXT NOT NULL,
                is_published INTEGER NOT NULL DEFAULT 0
                    CHECK (is_published IN (0, 1))
            )
            """
        )

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(resources)"
            ).fetchall()
        }

        if "is_published" not in columns:
            connection.execute(
                """
                ALTER TABLE resources
                ADD COLUMN is_published INTEGER NOT NULL DEFAULT 0
                CHECK (is_published IN (0, 1))
                """
            )

        if "available_from" not in columns:
            connection.execute(
                """
                ALTER TABLE resources
                ADD COLUMN available_from TEXT
                """
            )


def save_resource(
    waste_type,
    quantity_kg,
    location,
    condition,
    available_from=None,
):
    waste_type = waste_type.strip()
    location = location.strip()

    if not waste_type:
        raise ValueError("Waste type cannot be empty.")

    if quantity_kg <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if not location:
        raise ValueError("Location cannot be empty.")

    if available_from is not None:
        if isinstance(available_from, date):
            available_from = available_from.isoformat()
        else:
            raise ValueError("Availability date must be a date.")

    resource_id = str(uuid4())
    registered_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO resources (
                resource_id,
                waste_type,
                quantity_kg,
                location,
                condition,
                registered_at,
                is_published,
                available_from
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                resource_id,
                waste_type,
                quantity_kg,
                location,
                condition,
                registered_at,
                available_from,
            ),
        )

    return resource_id


def publish_resource(resource_id, published=True):
    if not isinstance(published, bool):
        raise ValueError("Published status must be True or False.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE resources
            SET is_published = ?
            WHERE resource_id = ?
            """,
            (int(published), resource_id),
        )

        return cursor.rowcount == 1


def get_all_resources():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT resource_id, waste_type, quantity_kg,
                   location, condition, registered_at,
                   is_published, available_from
            FROM resources
            ORDER BY registered_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_public_resources():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT resource_id, waste_type, quantity_kg,
                   location, condition, registered_at,
                   available_from
            FROM resources
            WHERE is_published = 1
            ORDER BY registered_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
