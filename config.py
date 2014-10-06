import os
basedir = os.path.abspath(os.path.dirname(__file__))



class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    USER_PER_PAGE = 10
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://ashnet:Uno12mazurca@localhost/datadev')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
   
        SQLALCHEMY_RECORD_QUERIES = True
    print SQLALCHEMY_DATABASE_URI

    
class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://ashnet:Uno12mazurca@localhost/datadev')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
        SQLALCHEMY_RECORD_QUERIES = True
       
 

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = '3daTdaT12T'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.db')



class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://ashnet:Uno12mazurca@localhost/datadev') 
       
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        SQLALCHEMY_RECORD_QUERIES = True
      
    
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

    'default': DevelopmentConfig
}


