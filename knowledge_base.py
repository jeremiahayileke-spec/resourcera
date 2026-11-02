import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "resourcera.db"


def initialize_knowledge_base():
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_catalog (
                material_id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_name TEXT NOT NULL UNIQUE,
                aliases TEXT,
                description TEXT,
                common_sources TEXT,
                handling_requirements TEXT,
                data_source TEXT,
                verification_status TEXT DEFAULT 'Unverified'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_pathways (
                pathway_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pathway_name TEXT NOT NULL UNIQUE,
                output_product TEXT NOT NULL,
                description TEXT,
                equipment_requirements TEXT,
                processing_requirements TEXT,
                safety_considerations TEXT,
                technology_maturity TEXT,
                data_source TEXT,
                verification_status TEXT DEFAULT 'Unverified'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_pathways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                pathway_id INTEGER NOT NULL,
                suitability TEXT,
                evidence_notes TEXT,
                FOREIGN KEY (material_id)
                    REFERENCES material_catalog(material_id),
                FOREIGN KEY (pathway_id)
                    REFERENCES processing_pathways(pathway_id),
                UNIQUE(material_id, pathway_id)
            )
        """)

        connection.commit()

    finally:
        connection.close()
    seed_knowledge_base()
def add_material(
    material_name,
    aliases="",
    description="",
    common_sources="",
    handling_requirements="",
    data_source="",
):
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            INSERT OR IGNORE INTO material_catalog (
                material_name,
                aliases,
                description,
                common_sources,
                handling_requirements,
                data_source,
                verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Unverified')
        """, (
            material_name,
            aliases,
            description,
            common_sources,
            handling_requirements,
            data_source,
        ))

        connection.commit()

    finally:
        connection.close()


def get_materials():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        return [
            dict(row)
            for row in connection.execute("""
                SELECT * FROM material_catalog
                ORDER BY material_name
            """).fetchall()
        ]

    finally:
        connection.close()


def add_processing_pathway(
    pathway_name,
    output_product,
    description="",
    equipment_requirements="",
    processing_requirements="",
    safety_considerations="",
    technology_maturity="",
    data_source="",
):
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            INSERT OR IGNORE INTO processing_pathways (
                pathway_name,
                output_product,
                description,
                equipment_requirements,
                processing_requirements,
                safety_considerations,
                technology_maturity,
                data_source,
                verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Unverified')
        """, (
            pathway_name,
            output_product,
            description,
            equipment_requirements,
            processing_requirements,
            safety_considerations,
            technology_maturity,
            data_source,
        ))

        connection.commit()

    finally:
        connection.close()


def get_processing_pathways():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        return [
            dict(row)
            for row in connection.execute("""
                SELECT * FROM processing_pathways
                ORDER BY pathway_name
            """).fetchall()
        ]

    finally:
        connection.close()


def link_material_to_pathway(
    material_name,
    pathway_name,
    suitability="Unassessed",
    evidence_notes="",
):
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT material_id FROM material_catalog WHERE material_name = ?",
            (material_name,),
        )
        material = cursor.fetchone()

        cursor.execute(
            "SELECT pathway_id FROM processing_pathways WHERE pathway_name = ?",
            (pathway_name,),
        )
        pathway = cursor.fetchone()

        if not material or not pathway:
            raise ValueError("Material or processing pathway not found.")

        cursor.execute("""
            INSERT OR IGNORE INTO material_pathways (
                material_id,
                pathway_id,
                suitability,
                evidence_notes
            )
            VALUES (?, ?, ?, ?)
        """, (
            material[0],
            pathway[0],
            suitability,
            evidence_notes,
        ))

        connection.commit()

    finally:
        connection.close()


def get_material_opportunities(material_name):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT
                m.material_name,
                p.pathway_name,
                p.output_product,
                p.description,
                mp.suitability,
                mp.evidence_notes,
                p.verification_status
            FROM material_pathways mp
            JOIN material_catalog m
                ON mp.material_id = m.material_id
            JOIN processing_pathways p
                ON mp.pathway_id = p.pathway_id
            WHERE LOWER(m.material_name) = LOWER(?)
            ORDER BY p.pathway_name
        """, (material_name,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()

def seed_knowledge_base():
    materials = [
        ("Cassava Peels", "Cassava waste", "Peel residue from cassava processing"),
        ("Rice Husks", "Rice hulls", "Outer covering separated during rice milling"),
        ("Maize Residues", "Corn stalks; maize stalks", "Crop residues from maize production"),
        ("Cocoa Pod Husks", "Cocoa husks", "Pod residues from cocoa processing"),
        ("Orange Peels", "Citrus peels", "Peel residues from orange processing"),
    ]

    for name, aliases, description in materials:
        add_material(
            material_name=name,
            aliases=aliases,
            description=description,
        )

    pathways = [
        ("Composting", "Organic compost", "Biological decomposition of suitable organic residues."),
        ("Anaerobic Digestion", "Biogas and digestate", "Microbial breakdown of organic material without oxygen."),
        ("Briquette Production", "Solid fuel briquettes", "Conversion of suitable biomass into compact fuel."),
        ("Animal Feed Processing", "Processed animal feed", "Conversion of suitable agricultural residues into feed ingredients."),
        ("Biochar Production", "Biochar", "Thermal conversion of suitable biomass under limited oxygen."),
    ]

    for name, product, description in pathways:
        add_processing_pathway(
            pathway_name=name,
            output_product=product,
            description=description,
        )

    connections = [
        ("Cassava Peels", "Composting"),
        ("Cassava Peels", "Animal Feed Processing"),
        ("Rice Husks", "Briquette Production"),
        ("Rice Husks", "Biochar Production"),
        ("Maize Residues", "Composting"),
        ("Maize Residues", "Briquette Production"),
        ("Cocoa Pod Husks", "Composting"),
        ("Cocoa Pod Husks", "Biochar Production"),
        ("Orange Peels", "Composting"),
        ("Orange Peels", "Anaerobic Digestion"),
    ]

    for material, pathway in connections:
        link_material_to_pathway(material, pathway)


if __name__ == "__main__":
    initialize_knowledge_base()
    seed_knowledge_base()
    print("Resourcera knowledge base initialized successfully.")

if __name__ == "__main__":
    initialize_knowledge_base()

    materials = [
        ("Cassava Peels", "Cassava waste", "Peel residue from cassava processing"),
        ("Rice Husks", "Rice hulls", "Outer covering separated during rice milling"),
        ("Maize Residues", "Corn stalks; maize stalks", "Crop residues from maize production"),
        ("Cocoa Pod Husks", "Cocoa husks", "Pod residues from cocoa processing"),
        ("Orange Peels", "Citrus peels", "Peel residues from orange processing"),
    ]

    for name, aliases, description in materials:
        add_material(
            material_name=name,
            aliases=aliases,
            description=description,
        )

    pathways = [
        (
            "Composting",
            "Organic compost",
            "Biological decomposition of suitable organic residues."
        ),
        (
            "Anaerobic Digestion",
            "Biogas and digestate",
            "Microbial breakdown of organic material without oxygen."
        ),
        (
            "Briquette Production",
            "Solid fuel briquettes",
            "Conversion of suitable biomass into compact fuel."
        ),
        (
            "Animal Feed Processing",
            "Processed animal feed",
            "Conversion of suitable agricultural residues into feed ingredients."
        ),
        (
            "Biochar Production",
            "Biochar",
            "Thermal conversion of suitable biomass under limited oxygen."
        ),
    ]

    for name, product, description in pathways:
        add_processing_pathway(
            pathway_name=name,
            output_product=product,
            description=description,
        )

    seed_knowledge_base()

    print(f"Processing pathways registered: {len(get_processing_pathways())}")

    connections = [
        ("Cassava Peels", "Composting"),
        ("Cassava Peels", "Animal Feed Processing"),
        ("Rice Husks", "Briquette Production"),
        ("Rice Husks", "Biochar Production"),
        ("Maize Residues", "Composting"),
        ("Maize Residues", "Briquette Production"),
        ("Cocoa Pod Husks", "Composting"),
        ("Cocoa Pod Husks", "Biochar Production"),
        ("Orange Peels", "Composting"),
        ("Orange Peels", "Anaerobic Digestion"),
    ]

    for material, pathway in connections:
        link_material_to_pathway(material, pathway)

    print(f"Material-pathway relationships registered: {len(connections)}")

    opportunities = get_material_opportunities("Rice Husks")

    print("\nRice Husk Processing Opportunities:")

    for opportunity in opportunities:
        print(
            f"- {opportunity['pathway_name']} "
            f"→ {opportunity['output_product']}"
        )


    print(f"Materials registered: {len(get_materials())}")
    print("Resourcera knowledge base initialized successfully.")