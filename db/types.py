import json
import pickle
from sqlalchemy.types import TypeDecorator, TEXT, BLOB

class JSONEncoded(TypeDecorator):
    """Stores Python objects as JSON text."""
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None


class PickleEncoded(TypeDecorator):
    """Stores arbitrary Python objects via pickle."""
    impl = BLOB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value)

    def process_result_value(self, value, dialect):
        return pickle.loads(value) if value is not None else None