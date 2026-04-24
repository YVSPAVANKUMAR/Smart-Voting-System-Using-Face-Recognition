import importlib
import os
import sys
import unittest
from contextlib import contextmanager


@contextmanager
def patched_environment(**updates):
    original = os.environ.copy()
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def load_mongo_db_module():
    sys.modules.pop("mongo_db", None)
    module = importlib.import_module("mongo_db")
    return importlib.reload(module)


class MongoDbConfigTests(unittest.TestCase):
    def test_import_allows_missing_mongodb_uri(self):
        with patched_environment(MONGODB_URI=None):
            module = load_mongo_db_module()

        self.assertIsNone(module.MONGODB_URI)

    def test_get_database_raises_clear_error_when_mongodb_uri_missing(self):
        with patched_environment(MONGODB_URI=None):
            module = load_mongo_db_module()

        with self.assertRaises(RuntimeError) as context:
            module.get_database()

        self.assertIn("MONGODB_URI is not configured", str(context.exception))

    def test_blank_database_name_falls_back_to_default(self):
        with patched_environment(
            MONGODB_URI="mongodb://localhost:27017",
            MONGODB_DB_NAME="   ",
        ):
            module = load_mongo_db_module()

        self.assertEqual(module.MONGODB_DB_NAME, "smart_voting_system")


if __name__ == "__main__":
    unittest.main()
