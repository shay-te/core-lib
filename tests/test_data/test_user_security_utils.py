import enum
from datetime import timedelta
from http import HTTPStatus
from sqlalchemy import Integer, Column, VARCHAR
from core_lib.cache.cache_decorator import Cache
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.user_security import UserSecurity
from tests.test_data.test_utils import connect_to_mem_db
from core_lib.web_helpers.request_response_helpers import response_status


# CRUD SETUP
class User(Base):
    __tablename__ = 'user_security'
    __table_args__ = {'extend_existing': True}

    class PolicyRoles(enum.Enum):
        ADMIN = 1
        DELETE = 2
        CREATE = 3
        UPDATE = 4
        USER = 5

    class Status(enum.Enum):
        ACTIVE = 1
        NOT_ACTIVE = 2
        DELETED = 3
        BAN = 4

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    role = Column('role', IntEnum(PolicyRoles), default=PolicyRoles.USER)
    status = Column('status', IntEnum(Status), default=Status.ACTIVE)


class UserDataAccess(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('username', str),
        ValueRuleValidator('email', str),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, User, connect_to_mem_db(), UserDataAccess.rules_validator)


# CRUD INIT
user_data_access = UserDataAccess()


@Cache(key='user_data_{u_id}', expire=timedelta(seconds=30))
def get_user(u_id):
    return result_to_dict(user_data_access.get(u_id))


# USER SECURITY SETUP
class SessionUser(object):
    def __init__(self, id: int, role: int, status: int):
        self.id = id
        self.role = role
        self.status = status

    def __dict__(self):
        return {'id': self.id, 'role': self.role, 'status': self.status}


def has_access(user_session, check_policies):
    user_role = user_session.role
    role = []
    status = User.Status.ACTIVE.value
    user_status = user_session.status
    for policy in check_policies:
        if type(policy) == User.Status:
            status = policy.value
        if type(policy) == User.PolicyRoles:
            role.append(policy.value)
    if not role:
        role.append(User.PolicyRoles.USER.value)
    if user_role <= max(role) and user_status == status:
        return True
    else:
        return False


class CustomerSecurity(UserSecurity):
    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        if not policies:
            return response_status(HTTPStatus.OK)
        elif has_access(session_obj, policies):
            return response_status(HTTPStatus.OK)
        else:
            return response_status(HTTPStatus.UNAUTHORIZED)

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['role'], session_data['status'])

    def generate_session_data(self, user) -> dict:
        return {'id': user['id'], 'email': user['email'], 'role': user['role'], 'status': user['status']}
