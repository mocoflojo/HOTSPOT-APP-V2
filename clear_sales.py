"""
Script para limpiar ventas de la base de datos
Soporta multi-router: puede limpiar ventas de un router específico o todos
"""
from app import app
from database import db, Sale, User, Router

def show_sales_by_router():
    """Muestra el conteo de ventas por router"""
    with app.app_context():
        routers = Router.query.all()
        
        print("\n" + "="*60)
        print("📊 VENTAS POR ROUTER")
        print("="*60)
        
        total_sales = 0
        for router in routers:
            sales_count = Sale.query.filter_by(router_id=router.id).count()
            total_sales += sales_count
            status = "🟢 Activo" if router.is_active else "⚪ Inactivo"
            print(f"\n{status} Router: {router.name}")
            print(f"   IP: {router.ip}")
            print(f"   Ventas: {sales_count}")
        
        # Ventas sin router asignado (legacy)
        orphan_sales = Sale.query.filter_by(router_id=None).count()
        if orphan_sales > 0:
            print(f"\n⚠️  Ventas sin router asignado: {orphan_sales}")
            total_sales += orphan_sales
        
        print("\n" + "-"*60)
        print(f"📈 TOTAL DE VENTAS: {total_sales}")
        print("="*60 + "\n")
        
        return routers, total_sales

def clear_all_sales():
    """Elimina TODAS las ventas de TODOS los routers"""
    with app.app_context():
        try:
            total_sales = Sale.query.count()
            total_users = User.query.count()
            
            if total_sales == 0:
                print("✅ No hay ventas para eliminar.")
                return
            
            print(f"\n⚠️  ADVERTENCIA: Esto eliminará TODAS las ventas ({total_sales} ventas).")
            print(f"   Los usuarios de login ({total_users}) NO se verán afectados.")
            print(f"   Los routers configurados NO se verán afectados.")
            respuesta = input("\n¿Deseas continuar? (si/no): ").strip().lower()
            
            if respuesta not in ['si', 's', 'yes', 'y']:
                print("❌ Operación cancelada.")
                return
            
            # Eliminar todas las ventas
            Sale.query.delete()
            db.session.commit()
            
            print("\n✅ ¡Ventas eliminadas exitosamente!")
            print(f"   - {total_sales} ventas fueron eliminadas")
            print(f"   - {total_users} usuarios de login se mantienen")
            print(f"   - Routers configurados se mantienen")
            print("\n🎉 Los reportes empezarán desde cero.\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al eliminar ventas: {e}\n")

def clear_router_sales(router_id):
    """Elimina ventas de un router específico"""
    with app.app_context():
        try:
            router = Router.query.get(router_id)
            if not router:
                print(f"\n❌ No se encontró el router con ID {router_id}\n")
                return
            
            sales_count = Sale.query.filter_by(router_id=router_id).count()
            
            if sales_count == 0:
                print(f"\n✅ El router '{router.name}' no tiene ventas para eliminar.\n")
                return
            
            print(f"\n⚠️  ADVERTENCIA: Esto eliminará {sales_count} ventas del router:")
            print(f"   Router: {router.name}")
            print(f"   IP: {router.ip}")
            respuesta = input("\n¿Deseas continuar? (si/no): ").strip().lower()
            
            if respuesta not in ['si', 's', 'yes', 'y']:
                print("❌ Operación cancelada.")
                return
            
            # Eliminar ventas del router específico
            Sale.query.filter_by(router_id=router_id).delete()
            db.session.commit()
            
            print(f"\n✅ ¡Ventas del router '{router.name}' eliminadas exitosamente!")
            print(f"   - {sales_count} ventas fueron eliminadas")
            print(f"   - Ventas de otros routers se mantienen intactas\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al eliminar ventas: {e}\n")

def clear_orphan_sales():
    """Elimina ventas sin router asignado (legacy)"""
    with app.app_context():
        try:
            orphan_sales = Sale.query.filter_by(router_id=None).count()
            
            if orphan_sales == 0:
                print("\n✅ No hay ventas sin router asignado.\n")
                return
            
            print(f"\n⚠️  Se encontraron {orphan_sales} ventas sin router asignado.")
            print("   Estas son ventas antiguas de antes de la implementación multi-router.")
            respuesta = input("\n¿Deseas eliminarlas? (si/no): ").strip().lower()
            
            if respuesta not in ['si', 's', 'yes', 'y']:
                print("❌ Operación cancelada.")
                return
            
            # Eliminar ventas huérfanas
            Sale.query.filter_by(router_id=None).delete()
            db.session.commit()
            
            print(f"\n✅ ¡Ventas huérfanas eliminadas exitosamente!")
            print(f"   - {orphan_sales} ventas fueron eliminadas\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al eliminar ventas: {e}\n")

def interactive_menu():
    """Menú interactivo para limpiar ventas"""
    with app.app_context():
        while True:
            # Mostrar ventas por router
            routers, total_sales = show_sales_by_router()
            
            if total_sales == 0:
                print("✅ No hay ventas para eliminar.")
                break
            
            print("OPCIONES:")
            print("1. Eliminar ventas de un router específico")
            print("2. Eliminar TODAS las ventas de TODOS los routers")
            print("3. Eliminar ventas sin router asignado (legacy)")
            print("4. Salir")
            
            opcion = input("\nSelecciona una opción (1-4): ").strip()
            
            if opcion == '1':
                # Mostrar routers disponibles
                print("\nRouters disponibles:")
                for i, router in enumerate(routers, 1):
                    sales_count = Sale.query.filter_by(router_id=router.id).count()
                    print(f"{i}. {router.name} ({router.ip}) - {sales_count} ventas")
                
                try:
                    router_num = int(input("\nSelecciona el número del router: ").strip())
                    if 1 <= router_num <= len(routers):
                        clear_router_sales(routers[router_num - 1].id)
                    else:
                        print("❌ Número de router inválido.")
                except ValueError:
                    print("❌ Entrada inválida.")
            
            elif opcion == '2':
                clear_all_sales()
                break
            
            elif opcion == '3':
                clear_orphan_sales()
            
            elif opcion == '4':
                print("\n👋 Saliendo...\n")
                break
            
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🗑️  LIMPIADOR DE VENTAS - HOTSPOT-APP V2.1")
    print("="*60)
    
    interactive_menu()
