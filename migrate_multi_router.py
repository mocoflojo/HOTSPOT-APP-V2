"""
Script de migración mejorado para agregar soporte multi-router
Maneja la migración de la base de datos existente
"""
from app import app
from database import db, Router, Sale, User
from config import ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD, HOTSPOT_DNS
import os

def migrate_to_multi_router():
    with app.app_context():
        print("📊 Verificando estado de la base de datos...")
        
        # Verificar si ya existe un router
        existing_router = Router.query.first()
        if existing_router:
            print("✅ Ya existe al menos un router en la base de datos.")
            print(f"   Router: {existing_router.name} ({existing_router.ip})")
            
            # Asociar ventas sin router
            sales_without_router = Sale.query.filter_by(router_id=None).all()
            if sales_without_router:
                for sale in sales_without_router:
                    sale.router_id = existing_router.id
                db.session.commit()
                print(f"✅ {len(sales_without_router)} ventas asociadas al router principal")
            return
        
        print("🔧 Creando nuevo router desde configuración actual...")
        
        # Crear router desde config.ini
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
        
        print("✅ Router migrado exitosamente!")
        print(f"   Nombre: {default_router.name}")
        print(f"   IP: {default_router.ip}")
        print(f"   DNS: {default_router.hotspot_dns}")
        
        # Asociar todas las ventas existentes con el router por defecto
        try:
            all_sales = Sale.query.all()
            if all_sales:
                for sale in all_sales:
                    if sale.router_id is None:
                        sale.router_id = default_router.id
                db.session.commit()
                print(f"✅ {len(all_sales)} ventas asociadas al router principal")
        except Exception as e:
            print(f"⚠️  Advertencia al asociar ventas: {e}")
            db.session.rollback()
        
        print("\n🎉 Migración completada exitosamente!")
        print("   Ahora puedes agregar más routers desde la interfaz web.")

def recreate_database():
    """Recrear la base de datos desde cero (CUIDADO: Borra todos los datos)"""
    with app.app_context():
        print("⚠️  ADVERTENCIA: Esto borrará TODOS los datos!")
        response = input("¿Estás seguro? Escribe 'SI' para continuar: ")
        if response != 'SI':
            print("❌ Operación cancelada")
            return
        
        # Borrar base de datos
        db_path = os.path.join('instance', 'users.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️  Base de datos eliminada")
        
        # Recrear todas las tablas
        db.create_all()
        print("✅ Tablas recreadas")
        
        # Ejecutar migración
        migrate_to_multi_router()

if __name__ == '__main__':
    print("🔄 Iniciando migración a multi-router...")
    print("=" * 50)
    
    # Primero intentar migración normal
    try:
        migrate_to_multi_router()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("\n💡 Opciones:")
        print("   1. Si tienes datos importantes, haz un backup primero")
        print("   2. Ejecuta: python migrate_multi_router.py --recreate")
        print("      (Esto borrará todos los datos y recreará la BD)")
    
    print("=" * 50)
