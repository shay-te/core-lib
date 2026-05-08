import unittest

from sqlalchemy import Column, Integer, String, literal
from sqlalchemy.ext.declarative import declarative_base

from core_lib.data_layers.data.join_config import JoinConfig

_Base = declarative_base()


class _LeftEntity(_Base):
    __tablename__ = 'test_left_entity'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer)
    name = Column(String(64))


class _RightEntity(_Base):
    __tablename__ = 'test_right_entity'
    id = Column(Integer, primary_key=True)
    label = Column(String(64))
    type = Column(Integer)


class TestJoinConfig(unittest.TestCase):

    def test_join_config_creation(self):
        join_config = JoinConfig(
            model=_RightEntity,
            join_condition=_LeftEntity.target_id == _RightEntity.id,
            columns=[_RightEntity.label, _RightEntity.type],
            condition=_RightEntity.type == 1,
            is_outer_join=True,
        )

        self.assertEqual(join_config.model, _RightEntity)
        self.assertEqual(join_config.columns, [_RightEntity.label, _RightEntity.type])
        self.assertTrue(join_config.is_outer_join)
        self.assertIsNotNone(join_config.condition)
        self.assertIsNotNone(join_config.join_condition)

    def test_join_config_default_values(self):
        join_config = JoinConfig(columns=[_RightEntity.label])

        self.assertFalse(join_config.is_outer_join)
        self.assertIsNone(join_config.model)
        self.assertIsNone(join_config.join_condition)
        self.assertIsNone(join_config.condition)

    def test_join_config_with_multiple_columns(self):
        columns = [_RightEntity.id, _RightEntity.label, _RightEntity.type]
        join_config = JoinConfig(
            model=_RightEntity,
            join_condition=_LeftEntity.target_id == _RightEntity.id,
            columns=columns,
            condition=_RightEntity.type == 1,
        )

        self.assertEqual(len(join_config.columns), 3)
        self.assertEqual(join_config.columns, columns)

    def test_join_config_condition_stored(self):
        condition = _RightEntity.type == 1
        join_config = JoinConfig(
            model=_RightEntity,
            join_condition=_LeftEntity.target_id == _RightEntity.id,
            columns=[_RightEntity.label],
            condition=condition,
        )
        self.assertIsNotNone(join_config.condition)

    def test_join_config_join_condition_stored(self):
        join_condition = _LeftEntity.target_id == _RightEntity.id
        join_config = JoinConfig(
            model=_RightEntity,
            join_condition=join_condition,
            columns=[_RightEntity.label],
        )
        self.assertIsNotNone(join_config.join_condition)

    def test_join_config_column_only_mode(self):
        """JoinConfig with only `columns` (model=None, join_condition=None) is the
        column-only mode used for correlated scalar subqueries — must not raise."""
        computed = literal(1).label('always_one')
        join_config = JoinConfig(columns=[computed])

        self.assertIsNone(join_config.model)
        self.assertIsNone(join_config.join_condition)
        self.assertEqual(len(join_config.columns), 1)


if __name__ == '__main__':
    unittest.main()
