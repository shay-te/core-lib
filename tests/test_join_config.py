import unittest

from sqlalchemy import Column, Integer, VARCHAR, and_, literal

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.join_config import JoinConfig
from tests.test_data.test_utils import connect_to_mem_db


# Test entities mirror the real-life shapes JoinConfig is used against in this
# workspace: a row pointing to one of two related tables via a target_id +
# target_type discriminator (the FormPageField → CustomField / UserFieldDefinition
# pattern from admin_form_service), and a simple owner-style inner-join target
# (the Task → AdminUser pattern from admin_task_service).

class _Item(Base):
    __tablename__ = 'test_join_config_item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(64))
    target_id = Column(Integer)
    target_type = Column(Integer)


class _CustomField(Base):
    __tablename__ = 'test_join_config_custom_field'
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(VARCHAR(64))
    type = Column(Integer)


class _UserField(Base):
    __tablename__ = 'test_join_config_user_field'
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(VARCHAR(64))
    type = Column(Integer)


CUSTOM_FIELD_TYPE = 1
USER_FIELD_TYPE = 2


class TestJoinConfig(unittest.TestCase):

    def test_join_config_creation(self):
        join_config = JoinConfig(
            model=_CustomField,
            join_condition=_Item.target_id == _CustomField.id,
            columns=[_CustomField.label, _CustomField.type],
            condition=_CustomField.type == 1,
            is_outer_join=True,
        )

        self.assertEqual(join_config.model, _CustomField)
        self.assertEqual(join_config.columns, [_CustomField.label, _CustomField.type])
        self.assertTrue(join_config.is_outer_join)
        self.assertIsNotNone(join_config.condition)
        self.assertIsNotNone(join_config.join_condition)

    def test_join_config_default_values(self):
        join_config = JoinConfig(columns=[_CustomField.label])

        self.assertFalse(join_config.is_outer_join)
        self.assertIsNone(join_config.model)
        self.assertIsNone(join_config.join_condition)
        self.assertIsNone(join_config.condition)

    def test_join_config_with_multiple_columns(self):
        columns = [_CustomField.id, _CustomField.label, _CustomField.type]
        join_config = JoinConfig(
            model=_CustomField,
            join_condition=_Item.target_id == _CustomField.id,
            columns=columns,
            condition=_CustomField.type == 1,
        )

        self.assertEqual(len(join_config.columns), 3)
        self.assertEqual(join_config.columns, columns)

    def test_join_config_condition_stored(self):
        condition = _CustomField.type == 1
        join_config = JoinConfig(
            model=_CustomField,
            join_condition=_Item.target_id == _CustomField.id,
            columns=[_CustomField.label],
            condition=condition,
        )
        self.assertIsNotNone(join_config.condition)

    def test_join_config_join_condition_stored(self):
        join_condition = _Item.target_id == _CustomField.id
        join_config = JoinConfig(
            model=_CustomField,
            join_condition=join_condition,
            columns=[_CustomField.label],
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


def _apply_joins(session, base_entity, joins):
    """Reference implementation: apply a list of JoinConfig objects to a query.

    Mirrors `form_page_field_data_access._apply_joins` (form-core-lib) and
    `task_data_access._build_query` (task-core-lib). Defined here so the
    integration tests below assert the JoinConfig contract end-to-end against
    a real SQL backend, not just the dataclass shape.
    """
    query = session.query(*list(base_entity.__table__.columns))
    for jc in joins or []:
        if not isinstance(jc, JoinConfig):
            continue

        if jc.columns:
            query = query.add_columns(*jc.columns)

        # Column-only mode: no JOIN, only contribute columns to the SELECT.
        if jc.model is None or jc.join_condition is None:
            continue

        effective_condition = (
            and_(jc.join_condition, jc.condition)
            if jc.condition is not None
            else jc.join_condition
        )
        if jc.is_outer_join:
            query = query.outerjoin(jc.model, effective_condition)
        else:
            query = query.join(jc.model, effective_condition)
    return query


class TestJoinConfigIntegration(unittest.TestCase):
    """Real-life scenario tests — apply JoinConfig to actual queries against an
    in-memory SQLite DB. Each test mirrors a pattern actually used by a
    consumer in this workspace (admin_form_service, admin_task_service)."""

    @classmethod
    def setUpClass(cls):
        cls.db = connect_to_mem_db()
        engine = cls.db.engine
        _Item.__table__.create(engine, checkfirst=True)
        _CustomField.__table__.create(engine, checkfirst=True)
        _UserField.__table__.create(engine, checkfirst=True)

    def setUp(self):
        # Wipe between tests so each scenario controls its own data.
        with self.db.get() as session:
            session.query(_Item).delete()
            session.query(_CustomField).delete()
            session.query(_UserField).delete()

    def test_inner_join_surfaces_joined_columns(self):
        """Owner-style inner join (admin_task_service._build_owner_join):
        joined columns appear on each result row alongside the base columns."""
        with self.db.get() as session:
            cf = _CustomField(label='Match Me', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='Item-1', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[
                    _CustomField.label.label('cf_label'),
                    _CustomField.id.label('cf_id'),
                ],
                is_outer_join=False,
            )
            results = _apply_joins(session, _Item, [join]).all()

        self.assertEqual(len(results), 1)
        row = dict(results[0]._mapping)
        self.assertEqual(row['name'], 'Item-1')
        self.assertEqual(row['cf_label'], 'Match Me')
        self.assertEqual(row['cf_id'], 1)

    def test_inner_join_excludes_unmatched_rows(self):
        """Inner-join semantics: rows whose target_id has no matching joined
        row are dropped from the result set entirely."""
        with self.db.get() as session:
            cf = _CustomField(label='Has Match', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='Matched', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.add(_Item(name='Orphan', target_id=999_999, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[_CustomField.label.label('cf_label')],
                is_outer_join=False,
            )
            results = _apply_joins(session, _Item, [join]).all()

        names = sorted(dict(r._mapping)['name'] for r in results)
        self.assertEqual(names, ['Matched'])

    def test_outer_join_keeps_unmatched_rows_with_nulls(self):
        """Outer-join semantics: rows without a matching join target are kept,
        with NULL for the joined columns."""
        with self.db.get() as session:
            cf = _CustomField(label='Has Match', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='Matched', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.add(_Item(name='Orphan', target_id=999_999, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[_CustomField.label.label('cf_label')],
                is_outer_join=True,
            )
            results = _apply_joins(session, _Item, [join]).all()

        rows = sorted([dict(r._mapping) for r in results], key=lambda r: r['name'])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['name'], 'Matched')
        self.assertEqual(rows[0]['cf_label'], 'Has Match')
        self.assertEqual(rows[1]['name'], 'Orphan')
        self.assertIsNone(rows[1]['cf_label'])

    def test_two_outer_joins_dispatched_by_target_type(self):
        """The admin_form_service._build_form_page_field_joins pattern: each
        row carries a `target_type` discriminator, and the same `target_id`
        column points into one of two related tables. Two outer JoinConfigs,
        each guarded by a target_type condition, route each row to exactly one
        of the joined tables. Custom-field rows have CustomField columns
        populated and UserField columns NULL — and vice versa."""
        with self.db.get() as session:
            cf = _CustomField(label='Cust', type=CUSTOM_FIELD_TYPE)
            uf = _UserField(label='User', type=USER_FIELD_TYPE)
            session.add_all([cf, uf])
            session.flush()
            session.add(_Item(name='cf-row', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.add(_Item(name='uf-row', target_id=uf.id, target_type=USER_FIELD_TYPE))
            session.flush()

            cf_join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[
                    _CustomField.label.label('cf_label'),
                    _CustomField.id.label('cf_id'),
                ],
                condition=_Item.target_type == CUSTOM_FIELD_TYPE,
                is_outer_join=True,
            )
            uf_join = JoinConfig(
                model=_UserField,
                join_condition=_Item.target_id == _UserField.id,
                columns=[
                    _UserField.label.label('uf_label'),
                    _UserField.id.label('uf_id'),
                ],
                condition=_Item.target_type == USER_FIELD_TYPE,
                is_outer_join=True,
            )
            results = _apply_joins(session, _Item, [cf_join, uf_join]).all()

        rows = {dict(r._mapping)['name']: dict(r._mapping) for r in results}
        self.assertEqual(len(rows), 2)
        # cf-row: CustomField columns populated, UserField NULL
        self.assertEqual(rows['cf-row']['cf_label'], 'Cust')
        self.assertIsNone(rows['cf-row']['uf_label'])
        # uf-row: UserField columns populated, CustomField NULL
        self.assertEqual(rows['uf-row']['uf_label'], 'User')
        self.assertIsNone(rows['uf-row']['cf_label'])

    def test_condition_is_anded_into_on_clause_not_where(self):
        """`condition` is AND-ed with `join_condition` in the ON clause (not as
        a WHERE), so outer-join semantics are preserved: rows that fail the
        condition keep NULL for the joined columns rather than being filtered
        out of the result. This is what makes the target_type-discriminator
        pattern in `test_two_outer_joins_dispatched_by_target_type` work."""
        with self.db.get() as session:
            cf = _CustomField(label='YES', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='matches-condition', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.add(_Item(name='fails-condition', target_id=cf.id, target_type=USER_FIELD_TYPE))
            session.flush()

            join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[_CustomField.label.label('cf_label')],
                condition=_Item.target_type == CUSTOM_FIELD_TYPE,
                is_outer_join=True,
            )
            results = _apply_joins(session, _Item, [join]).all()

        rows = {dict(r._mapping)['name']: dict(r._mapping) for r in results}
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows['matches-condition']['cf_label'], 'YES')
        # The condition fails for this row, but it still appears (proves the
        # condition is in the ON clause, not the WHERE).
        self.assertIsNone(rows['fails-condition']['cf_label'])

    def test_column_only_join_config_contributes_computed_column(self):
        """The admin_task_service._build_target_users_column pattern: a JoinConfig
        with no model/join_condition adds a computed column (literal here, a
        correlated scalar subquery in production) to the SELECT without
        performing any JOIN. Each row in the base set still appears."""
        with self.db.get() as session:
            session.add(_Item(name='only-row', target_id=None, target_type=None))
            session.flush()

            join = JoinConfig(columns=[literal(42).label('answer')])
            results = _apply_joins(session, _Item, [join]).all()

        self.assertEqual(len(results), 1)
        row = dict(results[0]._mapping)
        self.assertEqual(row['name'], 'only-row')
        self.assertEqual(row['answer'], 42)

    def test_column_only_alongside_real_join(self):
        """A JOIN-mode JoinConfig and a column-only JoinConfig combined in the
        same query — both contribute columns; only the JOIN-mode one performs
        a JOIN. This is exactly what admin_task_service does (owner JOIN +
        target_users column)."""
        with self.db.get() as session:
            cf = _CustomField(label='X', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='row', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            real_join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[_CustomField.label.label('cf_label')],
                is_outer_join=False,
            )
            computed = JoinConfig(columns=[literal('static').label('marker')])
            results = _apply_joins(session, _Item, [real_join, computed]).all()

        row = dict(results[0]._mapping)
        self.assertEqual(row['cf_label'], 'X')
        self.assertEqual(row['marker'], 'static')

    def test_non_join_config_items_silently_skipped(self):
        """The reference _apply_joins tolerates non-JoinConfig items (strings,
        None) interleaved with real JoinConfigs — same defensive behavior the
        production data-access methods use."""
        with self.db.get() as session:
            cf = _CustomField(label='Y', type=CUSTOM_FIELD_TYPE)
            session.add(cf)
            session.flush()
            session.add(_Item(name='row', target_id=cf.id, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            join = JoinConfig(
                model=_CustomField,
                join_condition=_Item.target_id == _CustomField.id,
                columns=[_CustomField.label.label('cf_label')],
                is_outer_join=False,
            )
            results = _apply_joins(session, _Item, ['not_a_join_config', join, None]).all()

        self.assertEqual(len(results), 1)
        self.assertEqual(dict(results[0]._mapping)['cf_label'], 'Y')

    def test_no_joins_returns_base_rows_only(self):
        """`joins=None` (or `joins=[]`) is a valid pass-through: the query
        returns the base entity's columns and nothing else."""
        with self.db.get() as session:
            session.add(_Item(name='solo', target_id=None, target_type=None))
            session.flush()

            results = _apply_joins(session, _Item, None).all()

        self.assertEqual(len(results), 1)
        row = dict(results[0]._mapping)
        self.assertEqual(row['name'], 'solo')
        # Only base columns present
        self.assertEqual(set(row.keys()), {'id', 'name', 'target_id', 'target_type'})


if __name__ == '__main__':
    unittest.main()
