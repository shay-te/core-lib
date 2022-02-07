from sqlalchemy import Column, Integer


class SoftDeleteTokenMixin(object):
    delete_token = Column(Integer, default=None)
    delete_token._creation_order = 9998
