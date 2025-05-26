from flask import Blueprint

ecom_bp = Blueprint('ecom', __name__)

from .ecom import *

__all__ = ['ecom_bp']