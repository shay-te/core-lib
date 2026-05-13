import sqlalchemy as sa


class IntEnum(sa.types.TypeDecorator):
    impl = sa.Integer
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        # Use `is not None` instead of `if value` so enums whose value is
        # 0 (or any other falsy int) round-trip correctly. The previous
        # implementation silently coerced 0-valued enum members to NULL.
        return value.value if value is not None else None

    def process_result_value(self, value, dialect):
        return self._enumtype(value) if value is not None else None
