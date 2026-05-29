from core.config import settings

db_params = {
    "dbname": settings.postgres_db,
    "user": settings.postgres_user,
    "password": settings.postgres_password,
    "host": settings.postgres_host,
    "port": settings.postgres_port,
}
