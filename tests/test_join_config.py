import unittest

from sqlalchemy import Column, Integer, VARCHAR, literal

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.join_config import JoinConfig, apply_join_configs
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


def _apply_joins(session, base_entity, joins):
    """Tiny wrapper that builds a base query and delegates to the shared
    ``apply_join_configs`` helper. The two-line wrapper matches what every
    data_access layer in this workspace does (form-core-lib, task-core-lib)."""
    return apply_join_configs(
        session.query(*list(base_entity.__table__.columns)),
        joins,
    )


class TestJoinConfig(unittest.TestCase):

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

    # ------------------------------------------------------------------
    # Test helpers (factories + fixtures) so each test reads as a small
    # delta from the defaults.
    # ------------------------------------------------------------------

    def _cf_join(self, *, is_outer=False, condition=None, columns=None):
        return JoinConfig(
            model=_CustomField,
            join_condition=_Item.target_id == _CustomField.id,
            columns=columns or [_CustomField.label.label('cf_label')],
            condition=condition,
            is_outer_join=is_outer,
        )

    def _uf_join(self, *, is_outer=False, condition=None, columns=None):
        return JoinConfig(
            model=_UserField,
            join_condition=_Item.target_id == _UserField.id,
            columns=columns or [_UserField.label.label('uf_label')],
            condition=condition,
            is_outer_join=is_outer,
        )

    def _seed_cf_item(self, session, cf_label='Match', item_name='Item-1', item_target_type=None):
        cf = _CustomField(label=cf_label, type=CUSTOM_FIELD_TYPE)
        session.add(cf)
        session.flush()
        session.add(_Item(
            name=item_name,
            target_id=cf.id,
            target_type=CUSTOM_FIELD_TYPE if item_target_type is None else item_target_type,
        ))
        session.flush()
        return cf

    @staticmethod
    def _rows(results):
        return [dict(r._mapping) for r in results]

    @staticmethod
    def _compiled_sql(query):
        """Compile a SQLAlchemy query to its literal SQL string (no
        parameter placeholders) for substring assertions."""
        return str(query.statement.compile(compile_kwargs={'literal_binds': True}))

    def _base_query(self, session):
        return session.query(*list(_Item.__table__.columns))

    def _sql_for_joins(self, joins):
        with self.db.get() as session:
            return self._compiled_sql(apply_join_configs(self._base_query(session), joins))

    # ------------------------------------------------------------------
    # Dataclass-shape tests
    # ------------------------------------------------------------------

    def test_join_config_creation(self):
        join_config = self._cf_join(
            condition=_CustomField.type == 1,
            columns=[_CustomField.label, _CustomField.type],
            is_outer=True,
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
        join_config = self._cf_join(condition=_CustomField.type == 1, columns=columns)

        self.assertEqual(len(join_config.columns), 3)
        self.assertEqual(join_config.columns, columns)

    def test_join_config_condition_stored(self):
        join_config = self._cf_join(condition=_CustomField.type == 1)
        self.assertIsNotNone(join_config.condition)

    def test_join_config_join_condition_stored(self):
        join_config = self._cf_join()
        self.assertIsNotNone(join_config.join_condition)

    def test_join_config_column_only_mode(self):
        """JoinConfig with only `columns` (model=None, join_condition=None) is the
        column-only mode used for correlated scalar subqueries — must not raise."""
        join_config = JoinConfig(columns=[literal(1).label('always_one')])

        self.assertIsNone(join_config.model)
        self.assertIsNone(join_config.join_condition)
        self.assertEqual(len(join_config.columns), 1)

    # ------------------------------------------------------------------
    # Integration tests — apply JoinConfig to actual queries against an
    # in-memory SQLite DB. Each test mirrors a pattern actually used by a
    # consumer in this workspace (admin_form_service, admin_task_service).
    # ------------------------------------------------------------------

    def test_inner_join_surfaces_joined_columns(self):
        """Owner-style inner join (admin_task_service._build_owner_join):
        joined columns appear on each result row alongside the base columns."""
        with self.db.get() as session:
            cf = self._seed_cf_item(session, cf_label='Match Me', item_name='Item-1')
            join = self._cf_join(columns=[
                _CustomField.label.label('cf_label'),
                _CustomField.id.label('cf_id'),
            ])
            results = self._rows(_apply_joins(session, _Item, [join]).all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Item-1')
        self.assertEqual(results[0]['cf_label'], 'Match Me')
        self.assertEqual(results[0]['cf_id'], cf.id)

    def test_inner_join_excludes_unmatched_rows(self):
        """Inner-join semantics: rows whose target_id has no matching joined
        row are dropped from the result set entirely."""
        with self.db.get() as session:
            self._seed_cf_item(session, cf_label='Has Match', item_name='Matched')
            session.add(_Item(name='Orphan', target_id=999_999, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            results = self._rows(_apply_joins(session, _Item, [self._cf_join()]).all())

        names = sorted(r['name'] for r in results)
        self.assertEqual(names, ['Matched'])

    def test_outer_join_keeps_unmatched_rows_with_nulls(self):
        """Outer-join semantics: rows without a matching join target are kept,
        with NULL for the joined columns."""
        with self.db.get() as session:
            self._seed_cf_item(session, cf_label='Has Match', item_name='Matched')
            session.add(_Item(name='Orphan', target_id=999_999, target_type=CUSTOM_FIELD_TYPE))
            session.flush()

            results = self._rows(_apply_joins(session, _Item, [self._cf_join(is_outer=True)]).all())

        rows = sorted(results, key=lambda r: r['name'])
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

            cf_join = self._cf_join(
                is_outer=True,
                condition=_Item.target_type == CUSTOM_FIELD_TYPE,
                columns=[
                    _CustomField.label.label('cf_label'),
                    _CustomField.id.label('cf_id'),
                ],
            )
            uf_join = self._uf_join(
                is_outer=True,
                condition=_Item.target_type == USER_FIELD_TYPE,
                columns=[
                    _UserField.label.label('uf_label'),
                    _UserField.id.label('uf_id'),
                ],
            )
            results = self._rows(_apply_joins(session, _Item, [cf_join, uf_join]).all())

        rows = {r['name']: r for r in results}
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
            cf = self._seed_cf_item(session, cf_label='YES', item_name='matches-condition')
            session.add(_Item(name='fails-condition', target_id=cf.id, target_type=USER_FIELD_TYPE))
            session.flush()

            join = self._cf_join(
                is_outer=True,
                condition=_Item.target_type == CUSTOM_FIELD_TYPE,
            )
            results = self._rows(_apply_joins(session, _Item, [join]).all())

        rows = {r['name']: r for r in results}
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
            results = self._rows(_apply_joins(session, _Item, [join]).all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'only-row')
        self.assertEqual(results[0]['answer'], 42)

    def test_column_only_alongside_real_join(self):
        """A JOIN-mode JoinConfig and a column-only JoinConfig combined in the
        same query — both contribute columns; only the JOIN-mode one performs
        a JOIN. This is exactly what admin_task_service does (owner JOIN +
        target_users column)."""
        with self.db.get() as session:
            self._seed_cf_item(session, cf_label='X', item_name='row')
            computed = JoinConfig(columns=[literal('static').label('marker')])
            results = self._rows(_apply_joins(session, _Item, [self._cf_join(), computed]).all())

        self.assertEqual(results[0]['cf_label'], 'X')
        self.assertEqual(results[0]['marker'], 'static')

    def test_non_join_config_items_silently_skipped(self):
        """The reference _apply_joins tolerates non-JoinConfig items (strings,
        None) interleaved with real JoinConfigs — same defensive behavior the
        production data-access methods use."""
        with self.db.get() as session:
            self._seed_cf_item(session, cf_label='Y', item_name='row')
            results = self._rows(_apply_joins(session, _Item, ['not_a_join_config', self._cf_join(), None]).all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['cf_label'], 'Y')

    def test_no_joins_returns_base_rows_only(self):
        """`joins=None` (or `joins=[]`) is a valid pass-through: the query
        returns the base entity's columns and nothing else."""
        with self.db.get() as session:
            session.add(_Item(name='solo', target_id=None, target_type=None))
            session.flush()

            results = self._rows(_apply_joins(session, _Item, None).all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'solo')
        # Only base columns present
        self.assertEqual(set(results[0].keys()), {'id', 'name', 'target_id', 'target_type'})

    # ------------------------------------------------------------------
    # SQL-shape tests — assert what `apply_join_configs` writes into the
    # query without running it. These guard against future regressions in
    # how the helper composes the SQL (JOIN type, ON clause, SELECT list).
    # ------------------------------------------------------------------

    def test_apply_join_configs_with_none_joins_returns_query_unchanged(self):
        with self.db.get() as session:
            base = self._base_query(session)
            result = apply_join_configs(base, None)
            self.assertIs(result, base)

    def test_apply_join_configs_with_empty_list_returns_query_unchanged(self):
        with self.db.get() as session:
            base = self._base_query(session)
            result = apply_join_configs(base, [])
            self.assertIs(result, base)

    def test_apply_join_configs_emits_inner_join_in_sql(self):
        sql = self._sql_for_joins([self._cf_join()])

        self.assertIn('JOIN test_join_config_custom_field', sql)
        self.assertNotIn('LEFT OUTER JOIN', sql)
        self.assertIn('test_join_config_item.target_id = test_join_config_custom_field.id', sql)

    def test_apply_join_configs_emits_left_outer_join_in_sql(self):
        sql = self._sql_for_joins([self._cf_join(is_outer=True)])

        self.assertIn('LEFT OUTER JOIN test_join_config_custom_field', sql)

    def test_apply_join_configs_adds_columns_to_select_list(self):
        join = self._cf_join(columns=[
            _CustomField.label.label('cf_label'),
            _CustomField.id.label('cf_id'),
        ])
        sql = self._sql_for_joins([join])

        self.assertIn('cf_label', sql)
        self.assertIn('cf_id', sql)
        # Base columns still in the SELECT
        self.assertIn('test_join_config_item.name', sql)

    def test_apply_join_configs_column_only_mode_omits_join_clause(self):
        column_only = JoinConfig(columns=[literal('hello').label('greeting')])
        sql = self._sql_for_joins([column_only])

        self.assertNotIn('JOIN', sql.upper().replace('JOIN_CONFIG', ''))
        self.assertIn('greeting', sql)
        # Base FROM is still the only FROM
        self.assertIn('FROM test_join_config_item', sql)

    def test_apply_join_configs_ands_condition_into_on_clause(self):
        join = self._cf_join(
            is_outer=True,
            condition=_Item.target_type == CUSTOM_FIELD_TYPE,
        )
        sql = self._sql_for_joins([join])

        # The condition is in the ON clause (between JOIN and the next clause),
        # not in a WHERE — `_Item.target_type = <value>` must appear between
        # 'ON' and (if present) 'WHERE'.
        on_idx = sql.find(' ON ')
        where_idx = sql.find(' WHERE ')
        self.assertGreater(on_idx, -1, f'Expected ON clause in: {sql}')
        condition_idx = sql.find('test_join_config_item.target_type = 1')
        self.assertGreater(
            condition_idx, on_idx,
            f'Expected condition after ON. SQL: {sql}',
        )
        if where_idx > -1:
            self.assertLess(
                condition_idx, where_idx,
                f'Condition should be in ON, not WHERE. SQL: {sql}',
            )

    def test_apply_join_configs_emits_each_join_for_multiple_join_configs(self):
        sql = self._sql_for_joins([
            self._cf_join(is_outer=True),
            self._uf_join(is_outer=True),
        ])

        self.assertIn('LEFT OUTER JOIN test_join_config_custom_field', sql)
        self.assertIn('LEFT OUTER JOIN test_join_config_user_field', sql)
        self.assertIn('cf_label', sql)
        self.assertIn('uf_label', sql)

    def test_apply_join_configs_skips_non_join_config_items_in_sql(self):
        sql = self._sql_for_joins(['not_a_join_config', self._cf_join(), None])

        # The single valid JoinConfig produced exactly one JOIN, not three.
        self.assertEqual(sql.count('JOIN test_join_config_custom_field'), 1)
        self.assertNotIn('not_a_join_config', sql)

    def test_apply_join_configs_combined_join_and_column_only_in_sql(self):
        column_only = JoinConfig(columns=[literal('static').label('marker')])
        sql = self._sql_for_joins([self._cf_join(), column_only])

        # Real join produces a JOIN; column-only just contributes its label.
        self.assertEqual(sql.count('JOIN test_join_config_custom_field'), 1)
        self.assertIn('cf_label', sql)
        self.assertIn('marker', sql)


if __name__ == '__main__':
    unittest.main()
