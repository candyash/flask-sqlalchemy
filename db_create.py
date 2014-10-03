#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig
from flask import Flask
from app.models import User
import os.path
import app

@app.before_first_request
def initialize_database():
    
    db.create_all()
    db.session.add(User("candy", "candy@gmail.com", "123"))
    db.session.commit()


if not os.path.exists(ProductionConfig.SQLALCHEMY_MIGRATE_REPO ):
    api.create(ProductionConfig.SQLALCHEMY_MIGRATE_REPO, 'database_repository')
    api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI,ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO,
                        api.version(SQLALCHEMY_MIGRATE_REPO))

