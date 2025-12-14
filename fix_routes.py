"""
Script to fix the corrupted routes.py by inserting missing user management functions
"""

# The complete missing functions to insert
MISSING_FUNCTIONS = '''    limit_uptime_raw = request.form.get('limit_uptime', '')
    limit_uptime_mikrotik_format = parse_limit_uptime(limit_uptime_raw)
    if limit_uptime_mikrotik_format:
        params['limit-uptime'] = limit_uptime_mikrotik_format

    add_hotspot_user(**params)

    return redirect(url_for('main.list_users'))


@main_bp.route('/users')
@login_required
def list_users():
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. Los usuarios no pudieron ser cargados.", "danger")
        return render_template('users.html',
                               all_users=[],
                               profiles=[],
                               comments=[],
                               selected_profile='',
                               selected_comment='',
                               search_query='',
                               active_page='users',
                               filters_applied=False)

    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    all_users_from_mikrotik = get_hotspot_users()
    
    if all_users_from_mikrotik is None:
        all_users_from_mikrotik = []
        flash("No se pudieron cargar los usuarios del hotspot. Verifica la conexión con el router.", "danger")

    all_profiles_list = get_hotspot_profiles()
    profiles_for_dropdown = sorted([p['name'] for p in all_profiles_list]) if all_profiles_list else []

    comments = sorted(list(set(user.get('comment', '') for user in all_users_from_mikrotik if user.get('comment'))))

    # Determinar si algún filtro está activo
    filters_applied = bool(profile_filter or comment_filter or search_query)

    # Aplicar los filtros a la lista completa
    filtered_users_list = all_users_from_mikrotik
    if profile_filter:
        filtered_users_list = [user for user in filtered_users_list if user.get('profile') == profile_filter]
    if comment_filter:
        filtered_users_list = [user for user in filtered_users_list if user.get('comment') == comment_filter]
    if search_query:
        filtered_users_list = [user for user in filtered_users_list if search_query.lower() in user.get('name', '').lower()]

    # Formatear el uptime para mostrarlo amigablemente
    for user in filtered_users_list:
        user['uptime_formatted'] = format_uptime_display(user.get('uptime', '0s'))

    return render_template(
        'users.html',
        all_users=filtered_users_list,
        profiles=profiles_for_dropdown,
        comments=comments,
        selected_profile=profile_filter,
        selected_comment=comment_filter,
        search_query=search_query,
        active_page='users',
        filters_applied=filters_applied
    )

@main_bp.route('/edit_user/<user_id>')
@login_required
def edit_user_page(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    user_data = get_hotspot_user_by_id(user_id)
    if not user_data:
        return "Usuario no encontrado", 404

    profiles = get_hotspot_profiles()
    if profiles is None:
        profiles = []

    return render_template('edit_user.html', user_data=user_data, profiles=profiles, active_page='users')

@main_bp.route('/update_user/<user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue actualizado.", "danger")
        return redirect(url_for('main.list_users'))

    update_params = {
        'profile': request.form['profile'],
        'comment': request.form['comment']
    }
    new_password = request.form['password']
    if new_password:
        update_params['password'] = new_password

    limit_uptime_raw = request.form.get('limit_uptime', '')
    limit_uptime_mikrotik_format = parse_limit_uptime(limit_uptime_raw)
    if limit_uptime_mikrotik_format:
        update_params['limit-uptime'] = limit_uptime_mikrotik_format

    if set_hotspot_user(user_id, update_params):
        flash("Usuario actualizado exitosamente.", "success")
    else:
        flash("Error al actualizar el usuario.", "danger")

    return redirect(url_for('main.list_users'))

@main_bp.route('/delete_by_filter')
@login_required
def delete_by_filter():
    # Obtener los filtros para comprobar si alguno está activo
    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    # Si no hay ningún filtro aplicado, redirigir y mostrar un mensaje
    if not (profile_filter or comment_filter or search_query):
        flash("La eliminación por filtro requiere que se aplique al menos un criterio de búsqueda. Si desea eliminar todos los usuarios, primero filtre por un criterio que los incluya a todos (Ej. un comentario común a todos) y luego use este botón.", "info")
        return redirect(url_for('main.list_users'))

    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. Los usuarios no fueron eliminados.", "danger")
        return redirect(url_for('main.list_users'))

    all_users_list = get_hotspot_users()
    if all_users_list is None:
        all_users_list = []
        flash("No se pudieron cargar los usuarios para eliminar. Verifica la conexión con el router.", "danger")


    users_to_delete = all_users_list
    if profile_filter:
        users_to_delete = [user for user in users_to_delete if user.get('profile') == profile_filter]
    if comment_filter:
        users_to_delete = [user for user in users_to_delete if user.get('comment') == comment_filter]
    if search_query:
        users_to_delete = [user for user in users_to_delete if search_query.lower() in user.get('name', '').lower()]

    ids_to_delete = [user['id'] for user in users_to_delete if 'id' in user]
    
    # Si después de aplicar los filtros la lista está vacía, mostrar mensaje
    if not ids_to_delete:
        flash("No se encontraron usuarios que coincidan con los filtros para eliminar. Ningún usuario fue eliminado.", "warning")
        return redirect(url_for('main.list_users'))

    deleted_count = 0
    for user_id in ids_to_delete:
        if remove_hotspot_user(user_id):
            deleted_count += 1
    
    flash(f"Se eliminaron {deleted_count} de {len(ids_to_delete)} usuarios filtrados.", "success")

    return redirect(url_for('main.list_users'))

@main_bp.route('/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue eliminado.", "danger")
        return redirect(url_for('main.list_users'))

    if remove_hotspot_user(user_id):
        flash("Usuario eliminado exitosamente.", "success")
    else:
        flash("Error al eliminar el usuario.", "danger")

    return redirect(url_for('main.list_users'))

@main_bp.route('/active_users')
@login_required
def list_active_users():
'''

def fix_routes():
    """Fix the corrupted routes.py file"""
    routes_file = 'routes.py'
    
    # Read the current file
    with open(routes_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line with "'comment': request.form.get('comment', '')" in create_manual_user
    insert_index = None
    for i, line in enumerate(lines):
        if i > 350 and i < 365 and "'comment': request.form.get('comment', '')" in line:
            # Found the params dict in create_manual_user
            # Insert after the closing brace
            insert_index = i + 1
            break
    
    if insert_index is None:
        print("Could not find insertion point!")
        return False
    
    # Remove corrupted lines from insert_index to @main_bp.route('/disconnect_user
    end_index = None
    for i in range(insert_index, len(lines)):
        if "@main_bp.route('/disconnect_user" in lines[i]:
            end_index = i
            break
    
    if end_index is None:
        print("Could not find end point!")
        return False
    
    # Create new content
    new_lines = lines[:insert_index] + ['\n' + MISSING_FUNCTIONS + '\n'] + lines[end_index:]
    
    # Write back
    with open(routes_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✓ Fixed routes.py - inserted missing functions at line {insert_index}")
    print(f"✓ Removed corrupted lines {insert_index} to {end_index}")
    return True

if __name__ == '__main__':
    if fix_routes():
        print("\n✓ routes.py has been fixed successfully!")
        print("✓ The list_users function with uptime formatting is now present")
        print("\nPlease restart your Flask app to apply the changes.")
    else:
        print("\n✗ Failed to fix routes.py")
