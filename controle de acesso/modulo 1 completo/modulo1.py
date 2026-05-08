# ======================================================
# IMPORTS
# ======================================================
import hashlib
import uuid
from datetime import datetime, timedelta

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean,
    DateTime, ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ======================================================
# BANCO DE DADOS
# ======================================================
DATABASE_URL = "sqlite:///app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ======================================================
# MODELOS
# ======================================================

# --- Associação Usuario ↔ Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("role_id", ForeignKey("roles.id"))
)

# --- Associação Role ↔ Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id")),
    Column("permission_id", ForeignKey("permissions.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary=user_roles)

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)

class SystemModule(Base):
    __tablename__ = "system_modules"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ======================================================
# CRIAR TABELAS
# ======================================================
Base.metadata.create_all(bind=engine)

# ======================================================
# SESSÃO / TOKEN
# ======================================================
class SessionManager:
    sessions = {}

    @classmethod
    def create(cls, user_id):
        token = str(uuid.uuid4())
        cls.sessions[token] = {
            "user_id": user_id,
            "expires": datetime.now() + timedelta(hours=2)
        }
        return token

    @classmethod
    def validate(cls, token):
        session = cls.sessions.get(token)
        if not session or session["expires"] < datetime.now():
            raise Exception("Sessão inválida")
        return session["user_id"]

# ======================================================
# AUDITORIA
# ======================================================
class AuditLogger:
    @staticmethod
    def log(user_id, action, status):
        db = SessionLocal()
        db.add(AuditLog(
            user_id=user_id,
            action=action,
            status=status
        ))
        db.commit()
        db.close()

# ======================================================
# AUTENTICAÇÃO
# ======================================================
class AuthenticationService:
    @staticmethod
    def login(username, password):
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()

        if not user or not user.check_password(password):
            AuditLogger.log(None, "LOGIN", "FALHA")
            db.close()
            raise Exception("Credenciais inválidas")

        token = SessionManager.create(user.id)
        AuditLogger.log(user.id, "LOGIN", "SUCESSO")
        db.close()
        return token

# ======================================================
# AUTORIZAÇÃO (RBAC)
# ======================================================
class AuthorizationService:
    @staticmethod
    def check_permission(user_id, permission_code):
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()

        for role in user.roles:
            perms = (
                db.query(Permission)
                .join(role_permissions)
                .filter(role_permissions.c.role_id == role.id)
            )
            if any(p.code == permission_code for p in perms):
                db.close()
                return True

        db.close()
        raise Exception("Acesso negado")

# ======================================================
# CRUD DE USUÁRIOS
# ======================================================
class UserRepository:
    @staticmethod
    def create(username, password):
        db = SessionLocal()
        user = User(
            username=username,
            password_hash=hashlib.sha256(password.encode()).hexdigest()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

# ======================================================
# CRUD DE MÓDULOS DO SISTEMA
# ======================================================
class SystemModuleRepository:
    @staticmethod
    def create(name, description):
        db = SessionLocal()
        module = SystemModule(name=name, description=description)
        db.add(module)
        db.commit()
        db.refresh(module)
        db.close()
        return module

# ======================================================
# CONFIGURAÇÃO INICIAL (SEED)
# ======================================================
def seed():
    db = SessionLocal()

    # Roles
    admin_role = Role(name="ADMIN")
    db.add(admin_role)

    # Permissões
    perm_user_create = Permission(code="SISTEMA.USUARIO.CRIAR")
    perm_module_create = Permission(code="SISTEMA.MODULO.CRIAR")
    db.add_all([perm_user_create, perm_module_create])

    db.commit()

    # Associa permissões ao role
    admin_role.permissions = [perm_user_create, perm_module_create]

    # Usuário admin
    admin = User(
        username="admin",
        password_hash=hashlib.sha256("123456".encode()).hexdigest()
    )
    admin.roles.append(admin_role)

    db.add(admin)
    db.commit()
    db.close()

# ======================================================
# EXEMPLO DE EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    seed()

    # Login
    token = AuthenticationService.login("admin", "123456")
    user_id = SessionManager.validate(token)

    # Criar usuário
    AuthorizationService.check_permission(user_id, "SISTEMA.USUARIO.CRIAR")
    UserRepository.create("joao", "senha123")

    # Criar módulo
    AuthorizationService.check_permission(user_id, "SISTEMA.MODULO.CRIAR")
    SystemModuleRepository.create(
        "FINANCEIRO",
        "Módulo Financeiro"
    )

    print("✅ Sistema inicializado com sucesso")
``