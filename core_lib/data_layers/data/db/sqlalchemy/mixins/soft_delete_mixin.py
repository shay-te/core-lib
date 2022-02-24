from datetime import datetime

from sqlalchemy import Column, DateTime, Integer


class SoftDeleteMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at._creation_order = 9998
    deleted_at = Column(DateTime, default=None)
    deleted_at._creation_order = 9998

    # def __init__(self, is_token_delete: bool):
    #     if is_token_delete:
    #         self.delete_token = Column(Integer, default=None)
    #         self.delete_token._creation_order = 9998


