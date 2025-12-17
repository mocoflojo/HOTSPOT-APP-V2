"""
Script para crear un usuario administrador inicial
"""
from app import app
from database import db, User

def create_admin_user():
    with app.app_context():
        # Verificar si ya existe un usuario
        existing_user = User.query.first()
        if existing_user:
            print(f"✅ Ya existe un usuario: {existing_user.username}")
            return
        
        # Crear usuario admin
        admin = User(username='admin')
        admin.set_password('admin')  # Cambiar esto en producción
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Usuario administrador creado!")
        print("   Usuario: admin")
        print("   Contraseña: admin")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")

if __name__ == '__main__':
    print("=" * 60)
    print("  CREAR USUARIO ADMINISTRADOR")
    print("=" * 60)
    create_admin_user()
    print("=" * 60)
