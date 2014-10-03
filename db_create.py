#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig
from app import db
import os.path

db.create_all()
if not os.path.exists(ProductionConfig.SQLALCHEMY_MIGRATE_REPO ):
    api.create(ProductionConfig.SQLALCHEMY_MIGRATE_REPO, 'database_repository')
    api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI,ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO,
                        api.version(SQLALCHEMY_MIGRATE_REPO))

