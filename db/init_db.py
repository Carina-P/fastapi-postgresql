import os
from pathlib import Path

import psycopg
from psycopg import ClientCursor


def main() -> None:
    if os.environ.get("DB_NAME") != "learning_test_db":
        raise RuntimeError("Database initialization only allowed for learning_test_db")
 
    db_dir = Path(__file__).resolve().parent
    schema = (db_dir / "schema.sql").read_text(encoding="utf-8")
    seed = (db_dir / "seed.sql").read_text(encoding="utf-8")

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    ) as conn:
        with ClientCursor(conn) as cur:
            cur.execute(schema)
            cur.execute(seed)

    print("Test database initialized successfully")


if __name__ == "__main__":
    main()
 