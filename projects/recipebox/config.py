# configurations
import os
import logging

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://pattylong:cat@localhost:5432/recipe'
    SECRET_KEY = os.urandom(32)
    LOGGING_LOCATION = 'recipe_app.log'
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
