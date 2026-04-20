from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
ckeditor = CKEditor()
login_manager = LoginManager()

# V-04 FIX: Rate limiter keyed by remote IP address.
limiter = Limiter(key_func=get_remote_address, default_limits=[])
