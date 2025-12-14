"""
Script para limpiar SOLO las ventas de la base de datos
Mantiene intactos los usuarios de login
"""
from app import app
from database import db, Sale, User

def clear_sales():
    """Elimina todas las ventas pero mantiene los usuarios de login"""
    with app.app_context():
        try:
            # Contar ventas antes de borrar
            total_sales = Sale.query.count()
            total_users = User.query.count()
            
            print(f"📊 Estado actual de la base de datos:")
            print(f"   - Ventas registradas: {total_sales}")
            print(f"   - Usuarios de login: {total_users}")
            print()
            
            if total_sales == 0:
                print("✅ No hay ventas para eliminar.")
                return
            
            # Confirmar acción
            print("⚠️  ADVERTENCIA: Esto eliminará TODAS las ventas registradas.")
            print("   Los usuarios de login NO se verán afectados.")
            respuesta = input("¿Deseas continuar? (si/no): ").strip().lower()
            
            if respuesta not in ['si', 's', 'yes', 'y']:
                print("❌ Operación cancelada.")
                return
            
            # Eliminar todas las ventas
            Sale.query.delete()
            db.session.commit()
            
            print()
            print("✅ ¡Ventas eliminadas exitosamente!")
            print(f"   - {total_sales} ventas fueron eliminadas")
            print(f"   - {total_users} usuarios de login se mantienen intactos")
            print()
            print("🎉 Ahora puedes usar la aplicación con el nuevo MikroTik")
            print("   Los reportes empezarán desde cero.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al eliminar ventas: {e}")

if __name__ == "__main__":
    clear_sales()
