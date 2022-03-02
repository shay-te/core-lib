from datetime import datetime

from sqlalchemy import Column, DateTime


class SoftDeleteMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at._creation_order = 9998
    deleted_at = Column(DateTime, default=None)
    deleted_at._creation_order = 9998
