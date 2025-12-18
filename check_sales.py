"""
Script para verificar ventas en la base de datos
"""
from app import app
from database import db, Sale, Router

def check_sales():
    """Verifica cuántas ventas hay por router"""
    with app.app_context():
        print("\n" + "="*60)
        print("📊 VERIFICACIÓN DE VENTAS")
        print("="*60)
        
        routers = Router.query.all()
        total_sales = 0
        
        for router in routers:
            sales_count = Sale.query.filter_by(router_id=router.id).count()
            total_sales += sales_count
            status = "🟢 Activo" if router.is_active else "⚪ Inactivo"
            print(f"\n{status} Router: {router.name}")
            print(f"   IP: {router.ip}")
            print(f"   Ventas: {sales_count}")
        
        # Ventas sin router
        orphan_sales = Sale.query.filter_by(router_id=None).count()
        if orphan_sales > 0:
            print(f"\n⚠️  Ventas sin router: {orphan_sales}")
            total_sales += orphan_sales
        
        print("\n" + "-"*60)
        print(f"📈 TOTAL DE VENTAS: {total_sales}")
        print("="*60 + "\n")

if __name__ == "__main__":
    check_sales()
