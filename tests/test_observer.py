import enum
import unittest
import datetime

from core_lib.core_lib import CoreLib
from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener
from core_lib.observer.observer_registry import ObserverRegistry
from core_lib.observer.observer_decorator import Observe


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class UserObserverListener(ObserverListener):
    EVENT = "EVENT"
    last_key = ""
    last_value = ""

    def update(self, key: str, value):
        UserObserverListener.last_key = key
        UserObserverListener.last_value = value


# with CoreLib Decorator
class TestObserverWithDecorator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main_observer = Observer(UserObserverListener())
        CoreLib.observer_registry.register("main", main_observer)

    def test_observer_string(self):
        self.set_observer("observe")
        self.assertEqual("observe", UserObserverListener.last_value['var'])
        self.set_observer("hello world")
        self.assertEqual("hello world", UserObserverListener.last_value['var'])

    def test_observer_float(self):
        self.set_observer(14)
        self.assertEqual(UserObserverListener.last_value['var'], 14)
        self.set_observer(14.0987)
        self.assertEqual(UserObserverListener.last_value['var'], 14.0987)

    def test_observer_bool(self):
        self.set_observer(True)
        self.assertEqual(UserObserverListener.last_value['var'], True)
        self.set_observer(False)
        self.assertEqual(UserObserverListener.last_value['var'], False)

    def test_observer_enum(self):
        self.set_observer(MyEnum.one)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.one)
        self.set_observer(MyEnum.two)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.two)
        self.set_observer(MyEnum.three)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.three)

    def test_observer_object(self):
        dat = datetime.date(2022, 1, 1)
        dct = {
            'date': dat,
            'tuple': ("fruit", "apple"),
            'list': ["fruit", "apple"]
        }
        self.set_observer(dct)
        self.assertEqual(dat, UserObserverListener.last_value['var']['date'])
        self.assertEqual(("fruit", "apple"), UserObserverListener.last_value['var']['tuple'])
        self.assertEqual(["fruit", "apple"], UserObserverListener.last_value['var']['list'])

    @Observe(event_key=UserObserverListener.EVENT, notify_before=False, observer_name="main")
    def set_observer(self, var):
        return var


# with observer registry
class TestObserverWithRegistry(unittest.TestCase):
    main_observer = Observer(UserObserverListener())

    @classmethod
    def setUpClass(cls):
        observer_factory = ObserverRegistry()
        observer_factory.register("main", TestObserverWithRegistry.main_observer)

    def test_observer_string(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, "observe")
        self.assertEqual("observe", UserObserverListener.last_value)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, "hello world")
        self.assertEqual("hello world", UserObserverListener.last_value)

    def test_observer_float(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, 14)
        self.assertEqual(UserObserverListener.last_value, 14)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, 14.0987)
        self.assertEqual(UserObserverListener.last_value, 14.0987)

    def test_observer_bool(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, True)
        self.assertEqual(UserObserverListener.last_value, True)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, False)
        self.assertEqual(UserObserverListener.last_value, False)

    def test_observer_enum(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.one)
        self.assertEqual(UserObserverListener.last_value, MyEnum.one)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.two)
        self.assertEqual(UserObserverListener.last_value, MyEnum.two)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.three)
        self.assertEqual(UserObserverListener.last_value, MyEnum.three)

    def test_observer_object(self):
        dat = datetime.date(2022, 1, 1)
        dct = {
            'date': dat,
            'tuple': ("fruit", "apple"),
            'list': ["fruit", "apple"],
        }
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, dct)
        self.assertEqual(dat, UserObserverListener.last_value['date'])
        self.assertEqual(("fruit", "apple"), UserObserverListener.last_value['tuple'])
        self.assertEqual(["fruit", "apple"], UserObserverListener.last_value['list'])
