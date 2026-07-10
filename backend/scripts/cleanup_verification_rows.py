from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> None:
    engine = create_engine(
        settings.database_url,
        connect_args={"connect_timeout": 10, "prepare_threshold": None},
    )

    with engine.begin() as conn:
        result = conn.execute(
            text("delete from hcp_interactions where hcp_name = :hcp_name"),
            {"hcp_name": "Dr. API Verification"},
        )

    print(f"deleted_rows={result.rowcount}")


if __name__ == "__main__":
    main()

