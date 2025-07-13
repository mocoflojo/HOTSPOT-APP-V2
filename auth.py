from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from database import db, User 

# Crear un Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__, template_folder='templates') 

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Verifica si ya existe algún usuario en la base de datos
    # Necesitamos current_app para acceder a la configuración y db.
    with current_app.app_context(): # Usar current_app para acceder a db en un contexto de aplicación
        users_exist_in_db = bool(User.query.first())
    
    # Si no existen usuarios y la petición NO es para el setup inicial, redirige al setup
    # Esto asegura que siempre se cree un usuario si no hay ninguno.
    if not users_exist_in_db and request.endpoint != 'auth.setup_initial_user':
        flash("Por favor, configura el primer usuario administrador.", "info")
        return redirect(url_for('auth.setup_initial_user'))

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) 

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard')) 
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html', active_page='login', users_exist=users_exist_in_db)
    
    return render_template('login.html', active_page='login', users_exist=users_exist_in_db)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

# --- RUTA TEMPORAL PARA CREAR EL PRIMER USUARIO ---
@auth_bp.route('/setup_initial_user', methods=['GET', 'POST'])
def setup_initial_user():
    # Verifica si ya existe algún usuario en la base de datos
    with current_app.app_context(): # Usar current_app para acceder a db
        if User.query.first(): 
            flash("Ya existe un usuario administrador. Por favor, inicia sesión.", "warning")
            return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or not confirm_password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('setup_initial_user.html')
        
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template('setup_initial_user.html')
        
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template('setup_initial_user.html')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit() 

        flash("¡Usuario administrador creado exitosamente! Ya puedes iniciar sesión.", "success")
        return redirect(url_for('auth.login'))

    return render_template('setup_initial_user.html')