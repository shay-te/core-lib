import datetime
import logging
from http import HTTPStatus

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.db_data_session_factory import DBDataSessionFactory
from core_lib.exceptions.status_code_exception import StatusCodeException
from core_lib.helpers.helpers import valid_email
from core_lib.validation.rule_validator import ValueRuleValidator, RuleValidator, ParameterRuleValidator
from examples.test_core_lib.core_lib.data_layers.data.db.user import User


user_rule_validators = [
    ValueRuleValidator(User.username.key, str, nullable=False),
    ValueRuleValidator(User.password.key, str, nullable=False),
    ValueRuleValidator(User.nick_name.key, str, nullable=False),
    ValueRuleValidator(User.first_name.key, str, nullable=False),
    ValueRuleValidator(User.middle_name.key, str),
    ValueRuleValidator(User.last_name.key, str),
    ValueRuleValidator(User.email.key, str, nullable=False, custom_validator=lambda value: valid_email(value)),  # email included in prohibited_keys, .
    ValueRuleValidator(User.birthday.key, datetime.date),
    ValueRuleValidator(User.gender.key,
                       User.Gender,
                       custom_converter=lambda value: User.Gender(value),  # Convert int to enum
                       custom_validator=lambda value: 0 <= value.value <= len(User.Gender))  # Working with enum after conversion.
]

user_rule_validator = RuleValidator(user_rule_validators)


class UserDataAccess(DataAccess):

    def __init__(self, db: DBDataSessionFactory):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    @ParameterRuleValidator('user_data', user_rule_validator)
    def create_user(self, user_data):
        with self.db.get_session() as session:
            user = User(**user_data)
            session.add(user)
        return user

    @ParameterRuleValidator('user_data', user_rule_validator, prohibited_keys=[User.email.key])
    def update_user(self, user_id: int, user_data: dict):
        with self.db.get_session() as session:
            return session.query(User).filter(User.id == user_id).update(user_data)

    def get_or_create_user(self, user_info):
        with self.db.get_session() as session:
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

    def get_user_by_id(self, user_id):
        with self.db.get_session() as session:
            user = session.query(User).get(user_id)
            if user:
                return user
            else:
                raise StatusCodeException(HTTPStatus.NOT_FOUND, 'User not found by id [{}]'.format(user_id))

