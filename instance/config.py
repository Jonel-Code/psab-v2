import os


class Config(object):
    """
    Common configurations
    """
    REPORTS_DIR = '/reports'
    REPORTS_JRXML_DIR = REPORTS_DIR + '/jrxml'
    REPORTS_OUTPUT_DIR = REPORTS_DIR + '/output'

    # Put any configurations here that are common across all environments


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


    # username = 'root'
    # password = 'root'
    # db_name = 'plmun-sab'
    # host = 'localhost'
    # port = '5432'
    #
    # SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}'


    username = 'zvxhwaiummjbwi'
    password = '588025bce883585b36325c864c561dcd09db7de40401b0615ccbcfb2eabbf71a'
    db_name = 'd36a9hvhc81vsr'
    host = 'ec2-184-73-216-48.compute-1.amazonaws.com'
    port = '5432'

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}?sslmode=require'

    SECRET_KEY = 'p9Bv<3Eid9%$i01'
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///instance/db_file/plmun_advising_db.db'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

    SECRET_KEY = 'p9Bv<3Eid9%$i01'

    # username = 'root'
    # password = 'root'
    # db_name = 'plmun-sab'
    # host = 'localhost'
    # port = '5432'
    #
    # SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}'

    username = 'zvxhwaiummjbwi'
    password = '588025bce883585b36325c864c561dcd09db7de40401b0615ccbcfb2eabbf71a'
    db_name = 'd36a9hvhc81vsr'
    host = 'ec2-184-73-216-48.compute-1.amazonaws.com'
    port = '5432'

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}?sslmode=require'

    # username = 'bd1221db'
    # password = '9ToEJWNnaK'
    # db_name = 'bd1221db'
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@www.db4free.net/{db_name}'
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///instance/db_file/plmun_advising_db.db'


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
