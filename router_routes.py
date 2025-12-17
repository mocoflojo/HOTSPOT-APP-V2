"""
Rutas para gestión de routers (multi-router support)
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from database import db, Router
from routes import get_active_router, set_active_router, get_all_active_routers

routers_bp = Blueprint('routers', __name__)

# ========== RUTAS DE GESTIÓN DE ROUTERS ==========

@routers_bp.route('/routers')
@login_required
def list_routers():
    """Página de gestión de routers"""
    routers = Router.query.order_by(Router.is_default.desc(), Router.name).all()
    active_router = get_active_router()
    return render_template('routers.html', 
                         routers=routers,
                         active_router=active_router,
                         active_page='routers')

@routers_bp.route('/routers/create', methods=['POST'])
@login_required
def create_router():
    """Crear un nuevo router"""
    name = request.form.get('name', '').strip()
    ip = request.form.get('ip', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    hotspot_dns = request.form.get('hotspot_dns', '10.5.50.1').strip()
    is_default = request.form.get('is_default') == 'on'
    
    if not all([name, ip, username, password]):
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for('routers.list_routers'))
    
    # Si se marca como default, quitar el default de los demás
    if is_default:
        Router.query.update({Router.is_default: False})
    
    new_router = Router(
        name=name,
        ip=ip,
        username=username,
        password=password,
        hotspot_dns=hotspot_dns,
        is_default=is_default,
        is_active=True
    )
    
    db.session.add(new_router)
    db.session.commit()
    
    flash(f"Router '{name}' creado exitosamente", "success")
    return redirect(url_for('routers.list_routers'))

@routers_bp.route('/routers/edit/<int:router_id>', methods=['GET', 'POST'])
@login_required
def edit_router(router_id):
    """Editar un router existente"""
    router = Router.query.get_or_404(router_id)
    
    if request.method == 'POST':
        router.name = request.form.get('name', '').strip()
        router.ip = request.form.get('ip', '').strip()
        router.username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if password:  # Solo actualizar si se proporciona nueva contraseña
            router.password = password
        router.hotspot_dns = request.form.get('hotspot_dns', '10.5.50.1').strip()
        is_default = request.form.get('is_default') == 'on'
        
        # Si se marca como default, quitar el default de los demás
        if is_default and not router.is_default:
            Router.query.filter(Router.id != router_id).update({Router.is_default: False})
            router.is_default = True
        elif not is_default and router.is_default:
            router.is_default = False
        
        db.session.commit()
        flash(f"Router '{router.name}' actualizado exitosamente", "success")
        return redirect(url_for('routers.list_routers'))
    
    return render_template('edit_router.html', router=router, active_page='routers')

@routers_bp.route('/routers/delete/<int:router_id>')
@login_required
def delete_router(router_id):
    """Eliminar un router"""
    router = Router.query.get_or_404(router_id)
    
    # No permitir eliminar si es el único router
    if Router.query.count() <= 1:
        flash("No puedes eliminar el único router. Crea otro primero.", "danger")
        return redirect(url_for('routers.list_routers'))
    
    # Si es el router activo, cambiar a otro
    if session.get('active_router_id') == router_id:
        other_router = Router.query.filter(Router.id != router_id).first()
        if other_router:
            set_active_router(other_router.id)
    
    router_name = router.name
    db.session.delete(router)
    db.session.commit()
    
    flash(f"Router '{router_name}' eliminado exitosamente", "success")
    return redirect(url_for('routers.list_routers'))

@routers_bp.route('/routers/toggle/<int:router_id>')
@login_required
def toggle_router(router_id):
    """Activar/Desactivar un router"""
    router = Router.query.get_or_404(router_id)
    
    # No permitir desactivar si es el único activo
    if router.is_active and Router.query.filter_by(is_active=True).count() <= 1:
        flash("No puedes desactivar el único router activo", "danger")
        return redirect(url_for('routers.list_routers'))
    
    router.is_active = not router.is_active
    db.session.commit()
    
    status = "activado" if router.is_active else "desactivado"
    flash(f"Router '{router.name}' {status}", "success")
    return redirect(url_for('routers.list_routers'))

@routers_bp.route('/routers/switch/<int:router_id>')
@login_required
def switch_router(router_id):
    """Cambiar al router especificado"""
    if set_active_router(router_id):
        router = Router.query.get(router_id)
        flash(f"Conectado a: {router.name}", "success")
    else:
        flash("No se pudo cambiar al router seleccionado", "danger")
    
    # Redirigir a la página anterior o al dashboard
    return redirect(request.referrer or url_for('main.dashboard'))

@routers_bp.route('/routers/test/<int:router_id>')
@login_required
def test_router(router_id):
    """Probar conexión con un router"""
    router = Router.query.get_or_404(router_id)
    
    try:
        import routeros_api
        api = routeros_api.RouterOsApiPool(
            router.ip,
            username=router.username,
            password=router.password,
            plaintext_login=True
        )
        connection = api.get_api()
        connection.disconnect()
        flash(f"✅ Conexión exitosa con '{router.name}'", "success")
    except Exception as e:
        flash(f"❌ Error al conectar con '{router.name}': {str(e)}", "danger")
    
    return redirect(url_for('routers.list_routers'))
