import click

from freekick.datastore._migrate import (
    _csv_to_sqlite_migration,
    create_db,
    create_db_table,
)


@click.command()
@click.option(
    "-c", "--create-database", help="Create DB", is_flag=True, default=False
)
@click.option(
    "-r",
    "--recreate-database",
    help="Re-create DB",
    is_flag=True,
    default=False,
)
@click.option(
    "-m",
    "--migrate-csv-to-db",
    help="Migrate from csv to db.",
    is_flag=True,
    default=False,
)
@click.option(
    "-t",
    "--create_table",
    help="Create a single table in DB.",
)
def cli(create_database, recreate_database, migrate_csv_to_db, create_table):
    if create_database:
        create_db(exists_ok=True)
    elif recreate_database:
        create_db(exists_ok=False)
    elif migrate_csv_to_db:
        _csv_to_sqlite_migration()
    if create_table:
        create_db_table(create_table)


if __name__ == "__main__":
    cli()
