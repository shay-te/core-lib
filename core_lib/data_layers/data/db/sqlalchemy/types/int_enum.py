import sqlalchemy as sa


class IntEnum(sa.types.TypeDecorator):
    impl = sa.Integer
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        """
        Initialize the IntEnum type decorator with an enum type.
        
        Parameters:
        	enumtype: The Python enum type to use for converting between database integers and enum members.
        """
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        """
        Validate and convert an enum member to its integer representation for database storage.
        
        Parameters:
            value: An enum member or `None` to be stored in the column.
        
        Returns:
            The integer value of the enum member, or `None` if the input is `None`.
        
        Raises:
            TypeError: If value is not an instance of the declared enum type and is not `None`.
        """
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
        """
        Convert a database integer value to a Python enum member.
        
        Parameters:
        	value: The integer value from the database.
        
        Returns:
        	The corresponding enum member, or None if the value is None.
        """
        return self._enumtype(value) if value is not None else None
