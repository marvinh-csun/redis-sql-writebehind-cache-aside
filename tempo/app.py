from flask import Flask
from cache import redis


def create_app():


    from flask_json import FlaskJSON
    from api.routes  import api_blueprint
    from db import db
    app = Flask(__name__,template_folder='templates')
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.config['UPLOAD_FOLDER'] = '/tmp'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sail:password@host.docker.internal:13305/laravel'
    json = FlaskJSON()
    json.init_app(app)
    db.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0",debug=True)