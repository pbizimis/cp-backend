from app.schemas.redisdb import RedisClient


def test_redisdb_get_client():
    """Unit test MongoDB client retrieval."""
    test_redisdb = RedisClient()
    test_redisdb.client = "mock_client"

    test_redisdb_client = test_redisdb.get_client()
    assert test_redisdb_client == "mock_client"
