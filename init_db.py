"""
Script completo de inicialización: crea router y usuario admin
"""
from app import app
from database import db, Router, User
from config import ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD, HOTSPOT_DNS

def initialize_database():
    with app.app_context():
        print("🔧 Creando estructura de base de datos...")
        db.create_all()
        print("✅ Tablas creadas\n")
        
        # 1. Crear router
        existing_router = Router.query.first()
        if not existing_router:
            print("📝 Creando router desde configuración...")
            default_router = Router(
                name="Router Principal",
                ip=ROUTER_IP,
                username=ROUTER_USER,
                password=ROUTER_PASSWORD,
                hotspot_dns=HOTSPOT_DNS,
                is_default=True,
                is_active=True
            )
            db.session.add(default_router)
            db.session.commit()
            print(f"✅ Router creado: {default_router.name} ({default_router.ip})\n")
        else:
            print(f"✅ Router ya existe: {existing_router.name}\n")
        
        # 2. Crear usuario admin
        existing_user = User.query.first()
        if not existing_user:
            print("👤 Creando usuario administrador...")
            admin = User(username='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado!")
            print("   Usuario: admin")
            print("   Contraseña: admin")
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login\n")
        else:
            print(f"✅ Usuario ya existe: {existing_user.username}\n")
        
        print("🎉 Inicialización completada!")
        print("   Puedes acceder a la aplicación en: http://localhost:5000")

if __name__ == '__main__':
    print("=" * 60)
    print("  INICIALIZACIÓN COMPLETA DE LA APLICACIÓN")
    print("=" * 60)
    initialize_database()
    print("=" * 60)
