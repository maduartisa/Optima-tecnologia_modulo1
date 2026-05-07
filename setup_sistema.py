# setup_sistema.py
from sistema_admin import criar_administrador, load_db
import os

# Criar admin padrão se não existir
db = load_db()

if not db["administradores"]:
    print("Criando administrador padrão...")
    admin = criar_administrador(
        nome="Administrador",
        email="admin@cnak.com",
        senha="admin123",
        perfil="super"
    )
    print(f"✓ Admin criado: {admin['nome']} ({admin['email']})")
else:
    print("✓ Administrador já existe")

print("\n🚀 Sistema pronto para uso!")
print("📝 Credenciais padrão:")
print("   Email: admin@cnak.com")
print("   Senha: admin123")