from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Inicializar SQLAlchemy (se inicializará con la app en app.py)
db = SQLAlchemy()

# Inicializar Flask-Login (se inicializará con la app en app.py)
login_manager = LoginManager()

# --- MODELO DE USUARIO PARA FLASK-LOGIN ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    last_router_id = db.Column(db.Integer, db.ForeignKey('router.id'), nullable=True)  # Último router usado

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# --- MODELO DE ROUTER ---
class Router(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nombre descriptivo (ej: "Router Sucursal A")
    ip = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    hotspot_dns = db.Column(db.String(100), default='10.5.50.1')
    is_default = db.Column(db.Boolean, default=False)  # Router por defecto
    is_active = db.Column(db.Boolean, default=True)  # Si está activo o deshabilitado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con ventas
    sales = db.relationship('Sale', backref='router', lazy=True)

    def __repr__(self):
        return f'<Router {self.name} ({self.ip})>'

# --- MODELO DE VENTAS ---
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(80), nullable=False)  # Removido unique=True para permitir mismo código en diferentes routers
    profile_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    router_id = db.Column(db.Integer, db.ForeignKey('router.id'), nullable=True)  # Asociar venta con router

    def __repr__(self):
        return f'<Sale {self.ticket_code} - {self.price}>'

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