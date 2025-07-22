import redis

def db_changed(sender, instance, **kwargs):
    if sender.__name__ not in ["Payment", "Enquiry", "Work", "Customer"]:
        return

    try:
        redis_client = redis.Redis()
        subscribers = redis_client.pubsub_numsub("dashboard_updates")[0][1]
        if subscribers > 0:
            redis_client.publish("dashboard_updates", "update")
        else:
            return
    except Exception as e:
        print("Redis publish failed:", str(e))
