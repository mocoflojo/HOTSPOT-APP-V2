"""
Script standalone para verificar ventas de la base de datos
Versión compilada - NO requiere Python
Muestra resumen de ventas por router
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configurar la aplicación Flask standalone
app = Flask(__name__)

# Obtener el directorio donde está el ejecutable
if getattr(sys, 'frozen', False):
    # Si está compilado con PyInstaller
    base_dir = os.path.dirname(sys.executable)
else:
    # Si se ejecuta como script Python
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Configurar la base de datos
db_path = os.path.join(base_dir, 'instance', 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Definir modelos (solo los necesarios)
class Router(db.Model):
    __tablename__ = 'router'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    router_id = db.Column(db.Integer, db.ForeignKey('router.id'), nullable=True)
    price = db.Column(db.Float, nullable=False)
    profile_name = db.Column(db.String(100))
    date_created = db.Column(db.DateTime)

def check_database():
    """Verifica que la base de datos exista"""
    if not os.path.exists(db_path):
        print(f"\n❌ ERROR: No se encontró la base de datos")
        print(f"   Ubicación esperada: {db_path}")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   1. Ejecuta HOTSPOT-APP.exe primero")
        print(f"   2. Haz login (esto crea la base de datos)")
        print(f"   3. Luego vuelve a ejecutar este script\n")
        input("Presiona Enter para salir...")
        sys.exit(1)

def show_sales_summary():
    """Muestra resumen detallado de ventas"""
    with app.app_context():
        routers = Router.query.all()
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE VENTAS - HOTSPOT-APP V2.1")
        print("="*70)
        
        total_sales_count = 0
        total_revenue = 0.0
        
        for router in routers:
            sales = Sale.query.filter_by(router_id=router.id).all()
            sales_count = len(sales)
            revenue = sum(sale.price for sale in sales)
            
            total_sales_count += sales_count
            total_revenue += revenue
            
            status = "🟢 Activo" if router.is_active else "⚪ Inactivo"
            print(f"\n{status} Router: {router.name}")
            print(f"   📍 IP: {router.ip}")
            print(f"   📊 Ventas: {sales_count}")
            print(f"   💰 Ingresos: ${revenue:,.2f}")
        
        # Ventas sin router asignado (legacy)
        orphan_sales = Sale.query.filter_by(router_id=None).all()
        if orphan_sales:
            orphan_count = len(orphan_sales)
            orphan_revenue = sum(sale.price for sale in orphan_sales)
            total_sales_count += orphan_count
            total_revenue += orphan_revenue
            
            print(f"\n⚠️  Ventas sin router asignado (legacy):")
            print(f"   📊 Ventas: {orphan_count}")
            print(f"   💰 Ingresos: ${orphan_revenue:,.2f}")
        
        print("\n" + "-"*70)
        print(f"📈 TOTAL GENERAL:")
        print(f"   📊 Total de ventas: {total_sales_count}")
        print(f"   💰 Ingresos totales: ${total_revenue:,.2f}")
        print("="*70 + "\n")
        
        return total_sales_count, total_revenue

def show_sales_by_profile():
    """Muestra ventas agrupadas por perfil"""
    with app.app_context():
        print("\n" + "="*70)
        print("📊 VENTAS POR PERFIL")
        print("="*70)
        
        # Obtener todos los perfiles únicos
        profiles = db.session.query(Sale.profile_name, 
                                   db.func.count(Sale.id).label('count'),
                                   db.func.sum(Sale.price).label('revenue'))\
                            .group_by(Sale.profile_name)\
                            .order_by(db.func.count(Sale.id).desc())\
                            .all()
        
        if not profiles:
            print("\n✅ No hay ventas registradas.\n")
            return
        
        for profile_name, count, revenue in profiles:
            print(f"\n📦 Perfil: {profile_name or 'Sin perfil'}")
            print(f"   📊 Ventas: {count}")
            print(f"   💰 Ingresos: ${revenue:,.2f}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 VERIFICADOR DE VENTAS - HOTSPOT-APP V2.1")
    print("="*70)
    print(f"📁 Directorio de trabajo: {base_dir}")
    print(f"💾 Base de datos: {db_path}")
    
    # Verificar que existe la base de datos
    check_database()
    
    try:
        # Mostrar resumen general
        total_sales, total_revenue = show_sales_summary()
        
        # Si hay ventas, mostrar por perfil
        if total_sales > 0:
            show_sales_by_profile()
        
        print("✅ Verificación completada.\n")
        input("Presiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
        input("Presiona Enter para salir...")
