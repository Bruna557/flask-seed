import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "1234")
    user, db_name = "users", "users"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
