#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig


api.upgrade(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig,SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))

