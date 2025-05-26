from flask import Blueprint
from .services.logic import ecom_bp
from .services.batch_logic import batch_bp

def init_app(app):
    app.register_blueprint(ecom_bp, url_prefix='/api/ecom')
    app.register_blueprint(batch_bp, url_prefix='/api/ecom/batch')