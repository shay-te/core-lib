from core_lib.cache.cache_decorator import Cache
from core_lib.connection.transaction_decorator import Transaction
from core_lib.data_layers.service.service import Service
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

CACHE_KEY_GROUP = 'core_lib_test_transaction_group_{group_id}'
TRANSACTION_TEST_CACHE = 'core_lib_test_transaction_cache'


class TransactionWidgetService(Service):

    def __init__(self, transaction_widget_data_access: TransactionWidgetDataAccess):
        self._transaction_widget_data_access = transaction_widget_data_access

    @Cache(CACHE_KEY_GROUP, handler_name=TRANSACTION_TEST_CACHE, invalidate=True)
    @DuplicateErrorHandler()
    @Transaction()
    def replace_group(self, group_id: int, names: list) -> list:
        self._transaction_widget_data_access.delete_group(group_id)
        for name in names:
            self._transaction_widget_data_access.create({
                TransactionWidget.group_id.key: group_id,
                TransactionWidget.name.key: name,
            })
        return self.list_group(group_id)

    @Cache(CACHE_KEY_GROUP, handler_name=TRANSACTION_TEST_CACHE)
    def list_group(self, group_id: int) -> list:
        return self._transaction_widget_data_access.names_in_group(group_id)
