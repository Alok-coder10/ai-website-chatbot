from sqlalchemy import text

class HealthService:

    async def database_health(self, db) -> bool:
        try:
            await db.execute(
                text("SELECT 1")
            )
            return True

        except Exception:
            return False


_health = None


def get_database_health_service():

    global _health

    if _health is None:
        _health = HealthService()

    return _health