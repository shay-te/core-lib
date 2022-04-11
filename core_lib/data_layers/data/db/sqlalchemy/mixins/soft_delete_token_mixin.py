from sqlalchemy import Column, Integer


class SoftDeleteTokenMixin(object):
    deleted_at_token = Column(Integer, default=0)
    deleted_at_token._creation_order = 9998
