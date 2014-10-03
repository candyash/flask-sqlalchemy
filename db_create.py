#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig
from flask import Flask
from app.models import User
from app import db
import os.path
from migrate.exceptions import DatabaseAlreadyControlledError
db.create_all()
user = User(email="candy@gmail.com", username="candy", password="test",
                is_admin=False)
db.session.add(user)
db.session.commit()


try:
    
    if not os.path.exists(ProductionConfig.SQLALCHEMY_MIGRATE_REPO ):
        api.create(ProductionConfig.SQLALCHEMY_MIGRATE_REPO, 'database_repository')
        api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI,ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO,
                            api.version(ProductionConfig.SQLALCHEMY_MIGRATE_REPO))

except DatabaseAlreadyControlledError:
            raise Exception('Database already initialized')