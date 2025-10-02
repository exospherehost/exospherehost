from app.config.settings import get_settings

def test_settings():
    settings = get_settings()
    print("✅ Loaded Settings:")
    print("Mongo URI:", settings.mongo_uri)
    print("Database:", settings.mongo_database_name)
    print("Trigger Workers:", settings.trigger_workers)
    print("Trigger Retention Days:", settings.trigger_retention_days)
    print("Cleanup Interval (minutes):", settings.cleanup_interval_minutes)

if __name__ == "__main__":
    test_settings()
