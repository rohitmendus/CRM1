import redis

def db_changed(sender, instance, **kwargs):
    print("Signal received")

    if sender.__name__ in ["User"]:
        return

    try:
        redis_client = redis.Redis()
        redis_client.publish("dashboard_updates", "update")
    except Exception as e:
        print("Redis publish failed:", str(e))
