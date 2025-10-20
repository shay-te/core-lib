import datetime
import logging
from http import HTTPStatus

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.validation import is_email, is_int_enum
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator
from examples.test_core_lib.core_lib.data_layers.data.db.user import User


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


class UserDataAccess(DataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    @ParameterRuleValidator(user_rule_validator, 'user_data')
    def create(self, user_data):
        with self.db.get() as session:
            user = User(**user_data)
            session.add(user)
        return user

    @ParameterRuleValidator(user_rule_validator, 'user_data', prohibited_keys=[User.email.key])
    def update(self, user_id: int, user_data: dict):
        with self.db.get() as session:
            return session.query(User).filter(User.id == user_id).update(user_data)

    def get_or_create_user(self, user_info):
        with self.db.get() as session:
            user = self.get_user_by_id(user_info['id'])
            if user:
                return user
            else:
                user = User()
                for key, value in user_info.items():
                    if key != 'id' and hasattr(user, key):
                        setattr(user, key, value)

                session.add(user)
        return user

    def get(self, user_id):
        with self.db.get() as session:
            user = session.query(User).get(user_id)
            if user:
                return user
            else:
                raise StatusCodeException(HTTPStatus.NOT_FOUND, f'User not found by id [{user_id}]')
