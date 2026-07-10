from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.database_url, connect_args={"connect_timeout": 10})

    with engine.connect() as conn:
        database, user = conn.execute(text("select current_database(), current_user")).one()
        tables = conn.execute(
            text(
                """
                select table_name
                from information_schema.tables
                where table_schema = 'public'
                order by table_name
                """
            )
        ).all()
        columns = conn.execute(
            text(
                """
                select column_name, data_type
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'hcp_interactions'
                order by ordinal_position
                """
            )
        ).all()
        revision = conn.execute(text("select version_num from alembic_version")).scalar_one_or_none()

    print(f"database={database}")
    print(f"user={user}")
    print(f"alembic_revision={revision}")
    print("tables=" + ",".join(row.table_name for row in tables))
    print("hcp_interactions_columns=" + ",".join(f"{row.column_name}:{row.data_type}" for row in columns))


if __name__ == "__main__":
    main()

