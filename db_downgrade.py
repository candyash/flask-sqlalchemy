#!flask/bin/python
from migrate.versioning import api
from config import ProductionConfig

v = api.db_version(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
api.downgrade(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO, v - 1)
v = api.db_version(ProductionConfig.SQLALCHEMY_DATABASE_URI, ProductionConfig.SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))

