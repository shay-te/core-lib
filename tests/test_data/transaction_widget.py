from sqlalchemy import Column, INTEGER, VARCHAR, Index

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class TransactionWidget(Base):

    __tablename__ = 'transaction_widget'

    INDEX_GROUP_NAME = 'uq_transaction_widget_group_name'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    group_id = Column(INTEGER, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)

    __table_args__ = (
        Index(INDEX_GROUP_NAME, 'group_id', 'name', unique=True),
    )
