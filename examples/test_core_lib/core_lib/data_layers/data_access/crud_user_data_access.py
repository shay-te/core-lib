import datetime

from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDataAccess
from core_lib.helpers.validation import is_email
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from examples.test_core_lib.core_lib.data_layers.data.db.user import User


class CrudUserDataAccess(CRUDSoftDataAccess):
    user_rule_validators = [
        ValueRuleValidator(User.username.key, str, nullable=False),
        ValueRuleValidator(User.password.key, str, nullable=False),
        ValueRuleValidator(User.nick_name.key, str, nullable=False),
        ValueRuleValidator(User.first_name.key, str, nullable=False),
        ValueRuleValidator(User.middle_name.key, str),
        ValueRuleValidator(User.last_name.key, str),
        # Email included in prohibited_keys.
        ValueRuleValidator(User.email.key, str, nullable=False, custom_validator=lambda value: is_email(value)),
        ValueRuleValidator(User.birthday.key, datetime.date),
        # Working with enum after conversion.
        ValueRuleValidator(
            User.gender.key,
            User.Gender,
            custom_converter=lambda value: User.Gender(value),  # Convert int to enum
            custom_validator=lambda value: 0 <= value.value <= len(User.Gender),
        ),
    ]

    user_rule_validator = RuleValidator(user_rule_validators)

    def __init__(self, db: SqlAlchemyDataHandlerRegistry):
        CRUD.__init__(self, User, db, CrudUserDataAccess.user_rule_validator)
