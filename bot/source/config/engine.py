import logging
import os
from sqlalchemy import create_engine


class InternalDatabaseConfiguration:
    DB_HOST = os.environ.get('DBHOST')
    DB_USER = os.environ.get('POSTGRES_USER')
    DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres'

    BATCH_SIZE = 1000

    engine = None

    @classmethod
    def get_engine(cls):
        if cls.engine is None:
            cls.engine = create_engine(
                cls.DB_URL,
                echo=False,
                executemany_mode='values',
                executemany_values_page_size=cls.BATCH_SIZE
            )
        return cls.engine
