from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializar SQLAlchemy (se inicializará con la app en app.py)
db = SQLAlchemy()

# Inicializar Flask-Login (se inicializará con la app en app.py)
login_manager = LoginManager()

# --- MODELO DE USUARIO PARA FLASK-LOGIN ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# user_loader para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db(app):
    """
    Inicializa la base de datos y el gestor de login con la aplicación Flask.
    Debe llamarse desde el archivo principal de la aplicación (app.py).
    """
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login' # Vista a la que redirigir si no está logueado