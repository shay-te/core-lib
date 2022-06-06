---
id: user_security
title: User Security
sidebar_label: User Security
---

`Core-Lib` has classes that provide user security implementations that users can tailor to their needs for authorization or authentication purposes.
These classes function together, and the user must implement them in order for `User Security` to work as expected.

Classes that handle `User Security`

# UserSecurity

*core_lib.session.user_security.UserSecurity* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L6)

`UserSecurity` is an abstract class that provides security functions to be implemented by the user as per their needs. Must be extended in the class where we will implement the abstract methods.

```python
class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
```

**Arguments**

- **`cookie_name`** *`(str)`*: Name of the cookie in which the token is passed
- **`token_handler`** *`(TokenHandler)`*: Expects a `TokenHandler` class that implements the `encode` and `decode` functions.

>`UserSecurity` token handler uses the `JWTTokenHandler` in `Core-Lib` which handles the [jwt](https://jwt.io) tokens. 



## Functions

### secure_entry()

*core_lib.session.user_security.UserSecurity.secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L14)

Is an abstract method that the user must implement, it can be customized to perform actions according 
to the `policies` supplied to the `RequireLogin` decorator.

```python
def secure_entry(self, request, session_obj, policies: list):
```

**Arguments**

- **`request`**: The received request object.
- **`session_obj`**: Decoded and formatted session data.
- **`policies`** *`(list)`*: List of policies that will be required for further authentication or authorization.

### from_session_data()

*core_lib.session.user_security.UserSecurity.from_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L19)

Also an abstract method to be implemented by the user, takes care of the formatting and 
cleaning of the decoded session data.

```python
def from_session_data(self, session_data: dict):
```

**Arguments**

- **`session_data`** *`(dict)`*: Decoded session data received from `_secure_entry()`.

### generate_session_data()

*core_lib.session.user_security.UserSecurity.generate_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L23)

Also an abstract method to be implemented by user, returns a structured `dict` with the received data that will be used in the response object.

```python
def generate_session_data(self, obj) -> dict:
```

**Arguments**

- **`obj`**: Data that must be structured and returned.

**Returns**

*`(dict)`*: Returns session data dictionary.


### generate_session_data_token()

*core_lib.session.user_security.UserSecurity.generate_session_data_token()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L26)

Is a method that will encode the data returned by `generate_session_data()` and return the encoded token.

```python
def generate_session_data_token(self, obj):
```

**Arguments**

- **`obj`**: That is being passed to `generate_session_data` in order to create a structured `dict`.

**Returns**

Returns encoded token.

### _secure_entry()

*core_lib.session.user_security.UserSecurity._secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/user_security.py#L38)

Is being called in the `@RequireLogin` decorator and is responsible for calling the `secure_entry` 
method that is implemented.

```python
def _secure_entry(self, request, policies):
```

**Arguments**

- **`request`**: Request object that is received by the decorator containing the cookie with token.

- **`policies`**: List of policies that will be passed to `secure_entry()`

**Returns**

Returns the data returned implemented `secure_entry()` function.


# SecurityHandler

*core_lib.session.security_handler.SecurityHandler* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/security_handler.py#L4)

`SecurityHandler` class registers our `UserSecurity` implemented class and is used to call `UserSecurity` methods using `get()`.

```python
class SecurityHandler(object):
```

## Functions

### register()

*core_lib.session.security_handler.SecurityHandler.register()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/security_handler.py#L8)

This function registers our `UserSecurity` implemented class.

```python
def register(user_security: UserSecurity):
```

**Arguments**

- **`user_security`** *`(UserSecurity)`*: `UserSecurity` implemented class.

### get()

*core_lib.session.security_handler.SecurityHandler.get()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/session/security_handler.py#L14)

This function returns the `UserSecurity` functions.

```python
def get() -> UserSecurity:
```

**Returns**

*`(UserSecurity)`*: Returns `UserSecurity` class object.


# RequireLogin Decorator

*core_lib.web_helpers.django.require_login.RequireLogin* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/web_helpers/django/require_login.py#L10)

This decorator with be responsible for authorization or authentication using `UserSecurity` functions and `SecurityHandler`.
It will accept `policies` from the user and `request` object from the function parameters, then the decorator will call the `_secure_entry` function and return the response.

```python
class RequireLogin(object):
    def __init__(self, policies: list = []):
```

**Arguments**

- **`policies`** *`(list)`* : List of policies which will be further passed on the the `UserSecurity` functions.


# UserAuthMiddleware

*core_lib.web_helpers.django.user_auth_middleware.UserAuthMiddleware* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/web_helpers/django/user_auth_middleware.py#L7)

This middleware can be configured in the `Django` settings in the `MIDDLEWARE` list. This middleware will simply verify if 
the specified cookie is present in the request, turn it to a `Session Object`, and append it to the `request.user` variable.

```python
class UserAuthMiddleware(MiddlewareMixin):
```

## Example

```python
import enum
from datetime import timedelta
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
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.django.require_login import RequireLogin
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
    def __init__(self, id: int, email: str, role: int, status: int):
        self.id = id
        self.email = email
        self.role = role
        self.status = status

    def __dict__(self):
        return {'id': self.id, 'email': self.email, 'role': self.role, 'status': self.status}


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
        return SessionUser(session_data['id'], session_data['email'], session_data['role'], session_data['status'])

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
@HandleException()
def admin_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
@HandleException()
def delete_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
@HandleException()
def create_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
@HandleException()
def update_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
@HandleException()
def user_entry(request):
    pass


@RequireLogin(policies=[])
@HandleException()
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
    is_authenticated = core_lib.auth.authnticate(email, password)
    if is_authenticated:
        user = ...
        get
        the
        user
        user_session = SecurityHandler.get().generate_session_data(user)
        response = response_json({'csrf_token': django.middleware.csrf.get_token(request), 'session': user_session})
        response.set_cookie(key=settings.COOKIE_NAME, value=SecurityHandler.get().generate_session_data_token(user))
        return response

```