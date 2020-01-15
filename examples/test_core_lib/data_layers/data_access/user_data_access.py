import datetime
import logging

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.rule_validator.validator import ValidationDictParameterByRules, RuleValidator
from core_lib.web_helpers.exceptions import NotFoundException
from examples.test_core_lib.data_layers.data.db.user import User

allowed_update_types = {
    User.birthday.key: RuleValidator(datetime.datetime, True),
    User.gender.key: RuleValidator(int, True, lambda value: 0 <= value <= len(User.Gender)),
}


class UserDataAccess(DataAccess):

    def __init__(self, data_sessions: list):
        DataAccess.__init__(data_sessions)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_user_by_id(self, user_id):
        with self.get_session() as session:
            user = session.query(User).get(user_id)
            if user:
                return user
            else:
                raise NotFoundException('User not found by id [{}]'.format(user_id))

    @ValidationDictParameterByRules(allowed_update_types, parameter_name='update')
    def update_user(self, user_id: int, update: dict):
        if 'gender' in update:
            update['gender']  = User.Gender(update['gender'])
        with self.get_session() as session:
            session.query(User).filter(User.id == user_id).update(update)

    def get_or_create_user(self, user_info):
        with self.get_session() as session:
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

