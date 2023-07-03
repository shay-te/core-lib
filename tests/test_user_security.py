import unittest
from datetime import timedelta, datetime
import jwt
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from tests.test_data.test_user_security_utils import CustomerSecurity, user_data_access, User, has_access

# SECURITY HANDLER REGISTER
secret_key = 'super-secret'
cookie_name = 'my_cookie_name'
security_handler = CustomerSecurity(cookie_name, secret_key, timedelta(seconds=30))
SecurityHandler.register(security_handler)


class TestUserSecurity(unittest.TestCase):
    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_user_security')

        cls.admin = result_to_dict(
            user_data_access.create({'username': 'admin', 'email': 'admin@def.com', 'role': User.PolicyRoles.ADMIN})
        )
        cls.delete = result_to_dict(
            user_data_access.create({'username': 'delete', 'email': 'delete@def.com', 'role': User.PolicyRoles.DELETE})
        )
        cls.create = result_to_dict(
            user_data_access.create({'username': 'create', 'email': 'create@def.com', 'role': User.PolicyRoles.CREATE})
        )
        cls.update = result_to_dict(
            user_data_access.create({'username': 'update', 'email': 'update@def.com', 'role': User.PolicyRoles.UPDATE})
        )
        cls.user = result_to_dict(
            user_data_access.create({'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER})
        )
        cls.user_ban = result_to_dict(
            user_data_access.create(
                {'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER, 'status': User.Status.BAN}
            )
        )
        cls.user_inactive = result_to_dict(
            user_data_access.create(
                {
                    'username': 'user',
                    'email': 'user@def.com',
                    'role': User.PolicyRoles.USER,
                    'status': User.Status.NOT_ACTIVE,
                }
            )
        )

        exp = datetime.now() + timedelta(seconds=30)
        cls.admin.update({'exp': exp})
        cls.delete.update({'exp': exp})
        cls.create.update({'exp': exp})
        cls.update.update({'exp': exp})
        cls.user.update({'exp': exp})
        cls.user_ban.update({'exp': exp})
        cls.user_inactive.update({'exp': exp})

        CoreLib.cache_registry.register('test_user_security', CacheHandlerRam())

    def test_has_access(self):
        self.assertTrue(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.ADMIN, User.Status.ACTIVE])
        )
        self.assertTrue(has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.DELETE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.create), [User.PolicyRoles.CREATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.UPDATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.USER]))

        self.assertFalse(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.ADMIN]))
        self.assertFalse(has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.DELETE]))
        self.assertFalse(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.CREATE]))
        self.assertFalse(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.ADMIN, User.Status.NOT_ACTIVE])
        )

        self.assertTrue(
            has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.USER, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.create), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )

        self.assertTrue(has_access(security_handler.from_session_data(self.admin), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.delete), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.create), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.update), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user), [User.Status.ACTIVE]))

    def test_session_data(self):
        time_stamp = datetime.utcnow().timestamp()
        user = result_to_dict(user_data_access.get(1))
        user_session = SecurityHandler.get().generate_session_data_token(user)
        decoded_dict = jwt.decode(user_session, options={"verify_signature": False})

        self.assertIsInstance(decoded_dict, dict)
        self.assertEqual(decoded_dict['id'], user['id'])
        self.assertEqual(decoded_dict['email'], user['email'])
        self.assertGreater(decoded_dict['exp'], time_stamp)
        self.assertEqual(int(decoded_dict['exp']), int(time_stamp) + 30)

