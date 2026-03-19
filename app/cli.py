from pathlib import Path

import click
from flask import current_app
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateIndex, CreateTable

from .extensions import db
from .services.seed_service import seed_sample_data


def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Create the SQLite database file and prepare the connection."""
        db_path = Path(current_app.config["SQLITE_DB_PATH"])
        db_path.parent.mkdir(parents=True, exist_ok=True)

        with db.engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys = ON;")

        db.create_all()
        click.echo(f"Database ready at {db_path}")

    @app.cli.command("dump-schema")
    def dump_schema_command():
        """Write the current SQLAlchemy schema to database/schema.sql."""
        schema_dir = Path(current_app.root_path).parent / "database"
        schema_path = schema_dir / "schema.sql"
        schema_dir.mkdir(parents=True, exist_ok=True)

        dialect = sqlite.dialect()
        statements = []

        for table in db.metadata.sorted_tables:
            statements.append(
                f"{str(CreateTable(table).compile(dialect=dialect)).rstrip()};"
            )
            for index in sorted(table.indexes, key=lambda item: item.name or ""):
                statements.append(
                    f"{str(CreateIndex(index).compile(dialect=dialect)).rstrip()};"
                )

        schema_path.write_text("\n\n".join(statements) + "\n", encoding="utf-8")
        click.echo(f"Schema written to {schema_path}")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed demo users, categories, sample products, and sample orders."""
        db_path = Path(current_app.config["SQLITE_DB_PATH"])
        db_path.parent.mkdir(parents=True, exist_ok=True)

        db.create_all()
        summary = seed_sample_data()

        click.echo("Seed data loaded.")
        click.echo(
            f"Users: {len(summary['users'])}, "
            f"Categories: {len(summary['categories'])}, "
            f"Products: {len(summary['products'])}, "
            f"Orders: {len(summary['orders'])}"
        )
        click.echo("Admin login: admin@gainzlab.local / Admin123!")
        click.echo("Customer login: customer@gainzlab.local / Customer123!")
