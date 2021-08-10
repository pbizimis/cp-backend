class RedisClient:
    """The Redis client class."""

    def __init__(self):
        self.client = None

    # Get method for FastAPI dependency injection
    def get_client(self):
        return self.client
