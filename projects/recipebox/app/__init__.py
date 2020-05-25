import os
import logging
import sys
sys.path.append("/Users/pattylong/Desktop/repo/udacity/FSND/projects/recipebox/app")
from flask import Flask, request, abort, jsonify, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#from flask_cors import CORS
#from models import setup_db, db_drop_and_create_all

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models

#db_drop_and_create_all(db)


# if __name__ == '__main__':
#     #APP.run(host='0.0.0.0', port=8080, debug=True)
#     APP.run()
