import logging

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.db_data_session_factory import DBDataSessionFactory
from core_lib.validation.rule_validator import ValueRuleValidator, RuleValidator, ParameterRuleValidator
from examples.demo_core_lib.core_lib.data_layers.data.db.demo_info import DemoInfo

demo_rule_validators = [
    ValueRuleValidator(DemoInfo.id.key, int),
    ValueRuleValidator(DemoInfo.demo_info_1.key, str),
    ValueRuleValidator(DemoInfo.demo_info_2.key, str),
    ValueRuleValidator(DemoInfo.demo_info_3.key, str),
    ValueRuleValidator(DemoInfo.demo_info_4.key, str),
    ValueRuleValidator(DemoInfo.demo_info_5.key, str),
    ValueRuleValidator(DemoInfo.demo_info_6.key, str)
]
demo_rule_validator = RuleValidator(demo_rule_validators)

class DemoDataAccess(DataAccess):

    def __init__(self, db: DBDataSessionFactory):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, data_data: dict):
        with self.db.get_session() as session:
            demo_info = DemoInfo(**data_data)
            session.add(demo_info)
        return demo_info

    @ParameterRuleValidator('demo_info', demo_rule_validator)
    def update(self, demo_id: int, demo_info: dict):
        with self.db.get_session() as session:
            return session.query(DemoInfo).filter(DemoInfo.id == demo_id).update(demo_info)
