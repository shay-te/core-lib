import sqlalchemy as sa


class IntEnum(sa.types.TypeDecorator):
    impl = sa.Integer
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # Enforce the column's declared enum type at the bind boundary.
        # Without this check, two enums with overlapping int values would
        # silently corrupt the column (write one type, read back the
        # other), and raw ints would fail later with a confusing
        # AttributeError deep inside SQLAlchemy.
        if not isinstance(value, self._enumtype):
            raise TypeError(
                f'IntEnum column expects a {self._enumtype.__name__} '
                f'member, got {type(value).__name__}'
            )
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value) if value is not None else None
