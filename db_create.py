#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig
from flask import Flask
from app.models import User
import os.path
from migrate.exceptions import DatabaseAlreadyControlledError



def initialize_database():
    try:
    
        db.create_all()
        db.session.add(User("candy", "candy@gmail.com", "123"))
        db.session.commit()
    except:
        flash ("database missing!!")

try:
    
    if not os.path.exists(ProductionConfig.SQLALCHEMY_MIGRATE_REPO ):
        api.create(ProductionConfig.SQLALCHEMY_MIGRATE_REPO, 'database_repository')
        api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI,ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO,
                            api.version(ProductionConfig.SQLALCHEMY_MIGRATE_REPO))

except DatabaseAlreadyControlledError:
            raise Exception('Database already initialized')