from flask import Blueprint

fast=Blueprint('fast', __name__)
from . import routes

from app.database import db_session
