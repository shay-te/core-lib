import datetime

from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.helpers.validation import is_email
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from examples.test_core_lib.core_lib.data_layers.data.db.user import User
from core_lib.helpers.validation import is_int_enum


def enum_gender_converter(value):
    if isinstance(value, str):
        return User.Gender.MALE if (value.lower() == 'male') else User.Gender.FEMALE
    else:
        return User.Gender(value)


user_rule_validators = [
    ValueRuleValidator(User.username.key, str, nullable=False),
    ValueRuleValidator(User.password.key, str, nullable=False),
    ValueRuleValidator(User.nick_name.key, str, nullable=False),
    ValueRuleValidator(User.first_name.key, str, nullable=False),
    ValueRuleValidator(User.middle_name.key, str),
    ValueRuleValidator(User.last_name.key, str),
    ValueRuleValidator(User.email.key, str, nullable=False, custom_validator=lambda value: is_email(value)),
    ValueRuleValidator(User.birthday.key, datetime.date),
    ValueRuleValidator(
        User.gender.key,
        int,
        custom_converter=lambda value: enum_gender_converter(value),
        custom_validator=lambda value: is_int_enum(value, User.Gender),
    ),
]

user_rule_validator = RuleValidator(user_rule_validators)


class CustomerDataAccess(CRUDSoftDeleteDataAccess):
    def __init__(self, db: SqlAlchemyConnectionRegistry):
        CRUD.__init__(self, User, db, user_rule_validator)
