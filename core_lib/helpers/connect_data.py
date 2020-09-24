import pysolr
from neo4j import GraphDatabase, basic_auth

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.handler.object_data_handler_factory import ObjectDataHandlerFactory
from sqlalchemy import create_engine
from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory


def connect_neo4j(config):
    neo4j_driver = GraphDatabase.driver(build_url(**config.url),
                                        auth=basic_auth(config.credentials.username,
                                                        config.credentials.password),
                                        encrypted=False)
    return ObjectDataHandlerFactory(neo4j_driver, new_session_callback=lambda driver: driver.session(), close_session_callback=lambda session: session.close())


def connect_sqlalchemy(config):
    engine = create_engine(build_url(**config.url),
                           pool_recycle=config.session.pool_recycle,
                           echo=config.log_queries)
    engine.connect()
    if config.create_db:
        Base.metadata.create_all(engine)
    return SqlAlchemyDataHandlerFactory(engine)


def connect_solr(config):
    solr_address = build_url(**config.url)
    return ObjectDataHandlerFactory(pysolr.Solr(solr_address, always_commit=True))
