import os
basedir = os.path.abspath(os.path.dirname(__file__))



class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\xbb\xed\x0e?\xcfY#8Ev\x17\x04t\x15\xa4\x8b\*******'
    USER_PER_PAGE = 3
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql+psycopg2://username:password@localhost/datadev')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
   
        SQLALCHEMY_RECORD_QUERIES = True
    print SQLALCHEMY_DATABASE_URI

    
class DevelopmentConfig(Config):
    DEBUG = True
           
 

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
   

class ProductionConfig(Config):
    DEBUG=False
   
     
    
class HerokuConfig(ProductionConfig):
    def init_app(cls,app):
        ProductionConfig.init_app(app)
        import logging
        from logging import StreamHandler
        file_handler=StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku':HerokuConfig,

    'default': DevelopmentConfig
}


