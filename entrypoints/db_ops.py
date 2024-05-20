import click

from freekick.database._migrate import _csv_to_sqlite_migration, create_db


@click.command()
@click.option("-c", "--create-database", help="Create DB", is_flag=True, default=False)
@click.option(
    "-r", "--recreate-database", help="Re-create DB", is_flag=True, default=False
)
@click.option(
    "-m",
    "--migrate-csv-to-db",
    help="Migrate from csv to db.",
    is_flag=True,
    default=False,
)
def cli(create_database, recreate_database, migrate_csv_to_db):
    if create_database:
        create_db(exists_ok=True)
    elif recreate_database:
        create_db(exists_ok=False)
    elif migrate_csv_to_db:
        _csv_to_sqlite_migration()


if __name__ == "__main__":
    cli()
