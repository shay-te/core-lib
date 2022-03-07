---
id: user_security
title: User Security
sidebar_label: User Security
---

`Core-Lib` has classes that provide user security implementations that the user may tailor to their needs for authorization or authentication purposes.
These classes function together, and the user must implement them in order for `User Security` to work as expected.

Classes that handle `User Security`
## UserSecurity
`UserSecurity` is an abstract class that provides security functions to be implemented by user as per their needs. Must be extended in the class where we will implement the abstract methods.

```python
class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
```
`cookie_name` (*str*) : name of the cookie in which the token is passed

`token_handler` : expects a `TokenHandler` class that implements the `encode` and `decode` functions.

>`UserSecurity` token handler uses the `JWTTokenHandler` in `Core-Lib` which handles the `jwt` tokens.



###Function provides by UserSecurity

- `secure_entry` is an abstract method that the user must implement, it can be customized to perform actions according to the `policies` supplied to the function.

```python
def secure_entry(self, request, session_obj, policies: list):
```
`request` :  the received request object.

`session_obj` : decoded and formatted session data.

`policies` (*list*) : list of policies that will be required for further authentication or authorization.

- `from_session_data` also an abstract method to be implemented by the user, takes care of the formatting and 
cleaning of the decoded session data.

```python
def from_session_data(self, session_data: dict):
```
`session_data` (*dict*) : decoded session data received from `_secure_entry()`.

- `generate_session_data` also an abstract method to be implemented by user, returns a structured `dict` with the received data that will be used in the response object.

```python
def generate_session_data(self, obj) -> dict:
```
`obj` : data that must be structured and returned.

- `generate_session_data_token` is a method that will encode the data returned by `generate_session_data()` and return the encoded token.

```python
def generate_session_data_token(self, obj):
```
`obj` that is being passed to `generate_session_data` in order to create a structured `dict`.

- `_secure_entry` is being called in the `@RequireLogin` decorator and is responsible for calling the `secure_entry` 
method that is implemented.

```python
def _secure_entry(self, request, policies):
```
`request` : request object that is received by the decorator containing the cookie with token.

`policies` : list of policies that will be passed to `secure_entry()`


## SecurityHandler
`SecurityHandler` class registers our `UserSecurity` implemented class and is used to call `UserSecurity` methods using `get()`.

```python
class SecurityHandler(object):
```

###Function provides by SecurityHandler

- `register` this function registers our `UserSecurity` implemented class.

```python
def register(user_security: UserSecurity):
```
`user_security` : `UserSecurity` implemented class.

- `get` this function returns the `UserSecurity` functions.

```python
def get() -> UserSecurity:
```


## RequireLogin Decorator
This decorator with be responsible for authorization or authentication using `UserSecurity` functions and `SecurityHandler`.
It will accept `poilicies` from the user and `request` object from the function parameters, then the decorator will call the `_secure_entry` function and return the response.
```python
class RequireLogin(object):
    def __init__(self, policies: list = []):
```
`policies` (*list*) : list of policies which will be further passed on the the `UserSecurity` functions.


## UserAuthMiddleware
This middleware can be configured in `Django` settings in the `MIDDLEWARE` list. This middleware will simply verify if 
the specified cookie is present in the request, turn it to a `Session Object`, and append it to `request.user` variable.

```python
class UserAuthMiddleware(MiddlewareMixin):
```

##Example
```python
import enum
from datetime import timedelta, datetime
from http import HTTPStatus

from django.conf import settings
from sqlalchemy import Integer, Column, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import handle_exceptions
from core_lib.web_helpers.django.decorators import RequireLogin
from core_lib.web_helpers.request_response_helpers import response_status


# CRUD SETUP
class User(Base):
    __tablename__ = 'user_security'

    class PolicyRoles(enum.Enum):
        ADMIN = 1
        DELETE = 2
        CREATE = 3
        UPDATE = 4
        USER = 5

    class Status(enum.Enum):
        ACTIVE = 1
        NOT_ACTIVE = 0

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
        CRUD.__init__(self, User, db_handler, UserDataAccess.rules_validator)


@Cache(key='user_data_{u_id}', expire=timedelta(seconds=30))
def get_user(u_id):
    return result_to_dict(user_data_access.get(u_id))


# USER SECURITY SETUP
class SessionUser(object):
    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email

    def __dict__(self):
        return {'id': self.id, 'email': self.email}


def has_access(user, check_policies):
    role = 5
    user_role = user['role']

    status = 1
    user_status = user['status']
    for policy in check_policies:
        if type(policy) == User.PolicyRoles:
            role = policy.value
        if type(policy) == User.Status:
            status = policy.value
    if user_role <= role and user_status == status:
        return True
    else:
        return False


class CustomerSecurity(UserSecurity):
    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        data_dict = get_user(session_obj.id)
        if data_dict['email'] == session_obj.email:
            if not policies:
                return response_status(HTTPStatus.OK)
            elif has_access(data_dict, policies):
                return response_status(HTTPStatus.OK)
            else:
                return response_status(HTTPStatus.UNAUTHORIZED)
        else:
            return response_status(HTTPStatus.FORBIDDEN)

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['email'])

    def generate_session_data(self, user) -> dict:
        return {
            'id': user['id'],
            'email': user['email'],
        }

# CRUD INIT
user_data_access = UserDataAccess()

# SECURITY HANDLER REGISTER
secret_key = 'super-secret'
security_handler = CustomerSecurity('user_cookie', secret_key, timedelta(seconds=2))
SecurityHandler.register(security_handler)


# IMPLEMENTATION
@RequireLogin(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
@handle_exceptions
def admin_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
@handle_exceptions
def delete_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
@handle_exceptions
def create_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
@handle_exceptions
def update_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
@handle_exceptions
def user_entry(request):
    pass


@RequireLogin(policies=[])
@handle_exceptions
def no_policy_entry(request):
    pass
# Function call with HttpRequest.COOKIES set as {'user_cookie': token}
# where token is the JWT encoded token which will be decoded by UserSecurity
# and the decoded object with data will be authenticated and authorized in secure_entry()
response = user_entry(request)

# Similarly, this process will happen with other function and the respective HTTP status code
# will be returned. This is how UserSecurity is implemented in Core-lib

# For authenticated user (Django example)
@csrf_exempt
@require_POST
def api_login(request):
    ...
    body = request_body_dict(request)
    email = body.get('email')
    password = body.get('pass')
    is_authenticated = auth_service.authnticate(email, password)
    if is_authenticagted:
        user = ... get the user
        user_session = SecurityHandler.get().generate_session_data(user)
        response = response_json({'csrf_token': django.middleware.csrf.get_token(request), 'session': user_session})
        response.set_cookie(key=settings.COOKIE_NAME, value=SecurityHandler.get().generate_session_data_token(user))
        return response    

```