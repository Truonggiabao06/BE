from infrastructure.databases.mssql import init_mssql, Base

def init_db(app):
    init_mssql(app)