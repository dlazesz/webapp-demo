from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, inspect
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = 'sqlite:///PrevCons.sqlite3'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, echo=False)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

# All tables imported automatically, but we need to create a mapping from names to objects to use them easily
table_objs = {table_name: Table(table_name, MetaData(), autoload_with=engine)
              for table_name in inspect(engine).get_table_names()}
table_column_objs = {(table_name, col_obj.key): col_obj for table_name, table_obj in table_objs.items()
                     for col_obj in table_obj.columns}


@contextmanager
def get_db():
    """Dependency vs. contextmanager
       INFO: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
       INFO: https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
