import os


class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True

    username = 'root'
    password = ''
    db_name = 'plmun_advising_db'

    SECRET_KEY = 'p9Bv<3Eid9%$i01'
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@localhost:3306/{db_name}'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///instance/db_file/plmun_advising_db.db'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False
    username = 'bd1221db'
    password = '9ToEJWNnaK'
    db_name = 'bd1221db'
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@www.db4free.net/{db_name}'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///instance/db_file/plmun_advising_db.db'


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
