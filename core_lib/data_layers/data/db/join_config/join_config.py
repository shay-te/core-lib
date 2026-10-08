from dataclasses import dataclass
from typing import Any


@dataclass
class JoinConfig:
    """Declarative SQL join / computed-column config consumed by data_access layers.

    Two modes:
      1. JOIN mode (model + join_condition set): data_access does
         query.join(model, join_condition AND condition) and adds `columns`.
      2. COLUMN-ONLY mode (model and join_condition both None): data_access
         only adds `columns` to the SELECT. Useful for correlated scalar
         subqueries / aggregated array columns where there's no real JOIN.

    Attributes:
        columns: list of SQLAlchemy column expressions. Computed columns must
                 carry a ``.label('...')`` so result_to_dict has a stable key.
        model: Optional SQLAlchemy entity class for JOIN mode.
        join_condition: Optional ON-clause expression for JOIN mode.
        condition: Optional WHERE-style expression AND-ed onto join_condition.
        is_outer_join: True for LEFT OUTER JOIN, False for INNER JOIN. Ignored
                       in COLUMN-ONLY mode.
    """
    columns: list
    model: Any = None
    join_condition: Any = None
    condition: Any = None
    is_outer_join: bool = False
