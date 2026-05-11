from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Query

from core_lib.data_layers.data.db.join_config.join_config import JoinConfig


def apply_join_configs(query: Query, joins: Optional[List[JoinConfig]]) -> Query:
    """Apply a list of JoinConfig objects to an existing SQLAlchemy query.

    Iterates `joins` and for each `JoinConfig`:
      - Adds its `columns` to the SELECT (when present).
      - In JOIN mode (model + join_condition set): AND-s `condition` into the
        ON clause and dispatches to `query.join(...)` or `query.outerjoin(...)`
        based on `is_outer_join`.
      - In COLUMN-ONLY mode (model and join_condition both None): only the
        columns are contributed; no JOIN is performed. Used for correlated
        scalar subqueries / aggregated array columns.

    Non-`JoinConfig` items in `joins` are silently skipped (so callers can
    interleave Nones / placeholders without guarding upstream).

    Args:
        query: An existing SQLAlchemy ``Query`` (typically
            ``session.query(*base_entity.__table__.columns)`` or
            ``session.query(BaseEntity)``).
        joins: Iterable of ``JoinConfig`` instances (or None / empty).

    Returns:
        The modified query. The original ``query`` is left untouched if
        ``joins`` is falsy or contains no valid JoinConfig items.
    """
    for join_config in joins or []:
        if not isinstance(join_config, JoinConfig):
            continue

        if join_config.columns:
            query = query.add_columns(*join_config.columns)

        if join_config.model is None or join_config.join_condition is None:
            continue

        effective_condition = (
            and_(join_config.join_condition, join_config.condition)
            if join_config.condition is not None
            else join_config.join_condition
        )
        if join_config.is_outer_join:
            query = query.outerjoin(join_config.model, effective_condition)
        else:
            query = query.join(join_config.model, effective_condition)
    return query
