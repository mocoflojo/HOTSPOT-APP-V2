"""
Script de Instalación Interactivo para HOTSPOT-APP
Configura la aplicación para un nuevo cliente
"""
from app import app
from database import db, Router, User
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 60)
    print("  HOTSPOT-APP - INSTALACIÓN PARA CLIENTE")
    print("=" * 60)
    print()

def get_router_info():
    """Solicita información del router al usuario"""
    print("📡 CONFIGURACIÓN DEL ROUTER PRINCIPAL")
    print("-" * 60)
    
    router_name = input("Nombre del router (ej: Router Principal): ").strip() or "Router Principal"
    router_ip = input("IP del router (ej: 192.168.88.1): ").strip()
    router_user = input("Usuario del router (ej: admin): ").strip()
    router_pass = input("Contraseña del router: ").strip()
    hotspot_dns = input("Hotspot DNS (default: 10.5.50.1): ").strip() or "10.5.50.1"
    
    return {
        'name': router_name,
        'ip': router_ip,
        'username': router_user,
        'password': router_pass,
        'hotspot_dns': hotspot_dns
    }

def get_admin_credentials():
    """Solicita credenciales del usuario administrador"""
    print("\n👤 CONFIGURACIÓN DEL USUARIO ADMINISTRADOR")
    print("-" * 60)
    
    admin_user = input("Nombre de usuario admin (default: admin): ").strip() or "admin"
    admin_pass = input("Contraseña admin (default: admin): ").strip() or "admin"
    
    return {
        'username': admin_user,
        'password': admin_pass
    }

def test_router_connection(router_info):
    """Prueba la conexión con el router"""
    print("\n🔍 Probando conexión con el router...")
    try:
        import routeros_api
        api = routeros_api.RouterOsApiPool(
            router_info['ip'],
            username=router_info['username'],
            password=router_info['password'],
            plaintext_login=True
        )
        connection = api.get_api()
        connection.disconnect()
        print("✅ Conexión exitosa!")
        return True
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        retry = input("\n¿Deseas continuar de todos modos? (s/n): ").lower()
        return retry == 's'

def install():
    clear_screen()
    print_header()
    
    # Verificar si ya existe una instalación
    db_path = os.path.join('instance', 'users.db')
    if os.path.exists(db_path):
        print("⚠️  ADVERTENCIA: Ya existe una base de datos.")
        print("   Si continúas, se eliminará y se creará una nueva.")
        confirm = input("\n¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
        if confirm != 'SI':
            print("\n❌ Instalación cancelada.")
            return
        os.remove(db_path)
        print("✅ Base de datos anterior eliminada.\n")
    
    # Obtener información del router
    router_info = get_router_info()
    
    # Validar que se ingresaron los datos mínimos
    if not router_info['ip'] or not router_info['username'] or not router_info['password']:
        print("\n❌ Error: Debes proporcionar al menos IP, usuario y contraseña del router.")
        return
    
    # Probar conexión (opcional pero recomendado)
    test = input("\n¿Deseas probar la conexión con el router? (s/n): ").lower()
    if test == 's':
        if not test_router_connection(router_info):
            print("\n❌ Instalación cancelada.")
            return
    
    # Obtener credenciales del admin
    admin_info = get_admin_credentials()
    
    # Confirmar instalación
    print("\n" + "=" * 60)
    print("  RESUMEN DE LA INSTALACIÓN")
    print("=" * 60)
    print(f"\n📡 Router:")
    print(f"   Nombre: {router_info['name']}")
    print(f"   IP: {router_info['ip']}")
    print(f"   Usuario: {router_info['username']}")
    print(f"   DNS: {router_info['hotspot_dns']}")
    print(f"\n👤 Usuario Admin:")
    print(f"   Usuario: {admin_info['username']}")
    print(f"   Contraseña: {'*' * len(admin_info['password'])}")
    
    confirm = input("\n¿Confirmas la instalación? (s/n): ").lower()
    if confirm != 's':
        print("\n❌ Instalación cancelada.")
        return
    
    # Crear base de datos e instalar
    print("\n🔧 Creando base de datos...")
    with app.app_context():
        db.create_all()
        print("✅ Base de datos creada")
        
        # Crear router
        print("\n📡 Configurando router...")
        router = Router(
            name=router_info['name'],
            ip=router_info['ip'],
            username=router_info['username'],
            password=router_info['password'],
            hotspot_dns=router_info['hotspot_dns'],
            is_default=True,
            is_active=True
        )
        db.session.add(router)
        db.session.commit()
        print(f"✅ Router '{router_info['name']}' configurado")
        
        # Crear usuario admin
        print("\n👤 Creando usuario administrador...")
        admin = User(username=admin_info['username'])
        admin.set_password(admin_info['password'])
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Usuario '{admin_info['username']}' creado")
    
    # Actualizar config.ini como backup
    print("\n📝 Actualizando config.ini como backup...")
    try:
        config_content = f"""[MIKROTIK]
ROUTER_IP = {router_info['ip']}
ROUTER_USER = {router_info['username']}
ROUTER_PASSWORD = {router_info['password']}

[HOTSPOT]
HOTSPOT_DNS = {router_info['hotspot_dns']}
"""
        with open('config.ini', 'w') as f:
            f.write(config_content)
        print("✅ config.ini actualizado")
    except Exception as e:
        print(f"⚠️  No se pudo actualizar config.ini: {e}")
    
    # Finalizar
    print("\n" + "=" * 60)
    print("  🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print(f"\n✅ Router configurado: {router_info['name']} ({router_info['ip']})")
    print(f"✅ Usuario admin: {admin_info['username']}")
    print("\n📌 PRÓXIMOS PASOS:")
    print("   1. Ejecuta: python app.py")
    print("   2. Accede a: http://localhost:5000")
    print(f"   3. Login con: {admin_info['username']} / {admin_info['password']}")
    print("\n⚠️  IMPORTANTE: Cambia la contraseña del admin después del primer login")
    print("=" * 60)

if __name__ == '__main__':
    try:
        install()
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error durante la instalación: {e}")
        print("   Por favor, contacta al soporte técnico.")
