# sistema_admin.py
import json
import os
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional
from hashlib import sha256

DB_FILE = "sistema_admin.json"
_lock = Lock()

DEFAULT_DB = {
    "administradores": [],      # admin: id, nome, email, senha_hash, perfil, ativo, created_at, logs
    "usuarios": [],             # usuario: id, nome, email, senha_hash, perfil, ativo, created_at, equipamentos
    "equipamentos": [],         # equipamento: id, nome, tipo, status, local, responsavel_id, created_at
    "sistemas": [],             # sistema: id, nome, versao, status, modulos, created_at
    "acessos": [],              # acesso: id, usuario_id, equipamento_id, timestamp, tipo
    "auditoria": []             # log: id, evento, entidade, entidade_id, usuario_id, detalhe, timestamp
}

def _ensure_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, indent=4, ensure_ascii=False)

def load_db() -> Dict[str, Any]:
    _ensure_db()
    with _lock:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_db(db: Dict[str, Any]):
    with _lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)

def hash_senha(senha: str) -> str:
    return sha256(senha.encode()).hexdigest()

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return hash_senha(senha) == senha_hash

def next_int_id(collection: list) -> int:
    ints = [item["id"] for item in collection if isinstance(item.get("id"), int)]
    return (max(ints) + 1) if ints else 1

def audit_log(evento: str, entidade: str, entidade_id: Any, usuario_id: Optional[int] = None, detalhe: dict = None):
    db = load_db()
    entry = {
        "id": next_int_id(db["auditoria"]),
        "evento": evento,
        "entidade": entidade,
        "entidade_id": entidade_id,
        "usuario_id": usuario_id,
        "detalhe": detalhe or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    db["auditoria"].append(entry)
    save_db(db)
    return entry

# ======================== ADMINISTRADORES ========================

def criar_administrador(nome: str, email: str, senha: str, perfil: str = "super") -> dict:
    db = load_db()
    novo_id = next_int_id(db["administradores"])
    admin = {
        "id": novo_id,
        "nome": nome,
        "email": email,
        "senha_hash": hash_senha(senha),
        "perfil": perfil,  # super, moderador
        "ativo": True,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "logs": []
    }
    db["administradores"].append(admin)
    save_db(db)
    audit_log("CREATE", "administrador", novo_id, None, {"nome": nome})
    return {k: v for k, v in admin.items() if k != "senha_hash"}

def autenticar_admin(email: str, senha: str) -> Optional[dict]:
    db = load_db()
    admin = next((a for a in db["administradores"] if a["email"] == email and a["ativo"]), None)
    if admin and verificar_senha(senha, admin["senha_hash"]):
        return {k: v for k, v in admin.items() if k != "senha_hash"}
    return None

def listar_administradores() -> List[dict]:
    db = load_db()
    return [{k: v for k, v in a.items() if k != "senha_hash"} for a in db["administradores"]]

# ======================== USUÁRIOS ========================

def criar_usuario(nome: str, email: str, senha: str, perfil: str = "operador") -> dict:
    db = load_db()
    novo_id = next_int_id(db["usuarios"])
    usuario = {
        "id": novo_id,
        "nome": nome,
        "email": email,
        "senha_hash": hash_senha(senha),
        "perfil": perfil,  # operador, supervisor
        "ativo": True,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "equipamentos": []
    }
    db["usuarios"].append(usuario)
    save_db(db)
    audit_log("CREATE", "usuario", novo_id, None, {"nome": nome, "email": email})
    return {k: v for k, v in usuario.items() if k != "senha_hash"}

def autenticar_usuario(email: str, senha: str) -> Optional[dict]:
    db = load_db()
    usuario = next((u for u in db["usuarios"] if u["email"] == email and u["ativo"]), None)
    if usuario and verificar_senha(senha, usuario["senha_hash"]):
        return {k: v for k, v in usuario.items() if k != "senha_hash"}
    return None

def obter_usuario(usuario_id: int) -> Optional[dict]:
    db = load_db()
    usuario = next((u for u in db["usuarios"] if u["id"] == usuario_id), None)
    return {k: v for k, v in usuario.items() if k != "senha_hash"} if usuario else None

def atualizar_usuario(usuario_id: int, dados: dict) -> Optional[dict]:
    db = load_db()
    usuario = next((u for u in db["usuarios"] if u["id"] == usuario_id), None)
    if usuario:
        if "senha" in dados:
            usuario["senha_hash"] = hash_senha(dados.pop("senha"))
        usuario.update(dados)
        save_db(db)
        audit_log("UPDATE", "usuario", usuario_id, None, dados)
        return {k: v for k, v in usuario.items() if k != "senha_hash"}
    return None

def deletar_usuario(usuario_id: int) -> bool:
    db = load_db()
    usuario = next((u for u in db["usuarios"] if u["id"] == usuario_id), None)
    if usuario:
        db["usuarios"].remove(usuario)
        save_db(db)
        audit_log("DELETE", "usuario", usuario_id)
        return True
    return False

def listar_usuarios() -> List[dict]:
    db = load_db()
    return [{k: v for k, v in u.items() if k != "senha_hash"} for u in db["usuarios"]]

# ======================== EQUIPAMENTOS ========================

def criar_equipamento(nome: str, tipo: str, local: str, responsavel_id: Optional[int] = None) -> dict:
    db = load_db()
    novo_id = next_int_id(db["equipamentos"])
    equipamento = {
        "id": novo_id,
        "nome": nome,
        "tipo": tipo,
        "status": "ativo",
        "local": local,
        "responsavel_id": responsavel_id,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    db["equipamentos"].append(equipamento)
    save_db(db)
    audit_log("CREATE", "equipamento", novo_id, responsavel_id, {"nome": nome})
    return equipamento

def obter_equipamento(equipamento_id: int) -> Optional[dict]:
    db = load_db()
    return next((e for e in db["equipamentos"] if e["id"] == equipamento_id), None)

def atualizar_equipamento(equipamento_id: int, dados: dict) -> Optional[dict]:
    db = load_db()
    equipamento = obter_equipamento(equipamento_id)
    if equipamento:
        equipamento.update(dados)
        save_db(db)
        audit_log("UPDATE", "equipamento", equipamento_id, None, dados)
        return equipamento
    return None

def deletar_equipamento(equipamento_id: int) -> bool:
    db = load_db()
    equipamento = obter_equipamento(equipamento_id)
    if equipamento:
        db["equipamentos"].remove(equipamento)
        save_db(db)
        audit_log("DELETE", "equipamento", equipamento_id)
        return True
    return False

def listar_equipamentos() -> List[dict]:
    db = load_db()
    return db["equipamentos"]

# ======================== ACESSOS ========================

def registrar_acesso(usuario_id: int, equipamento_id: int, tipo: str = "acesso") -> dict:
    db = load_db()
    novo_id = next_int_id(db["acessos"])
    acesso = {
        "id": novo_id,
        "usuario_id": usuario_id,
        "equipamento_id": equipamento_id,
        "tipo": tipo,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    db["acessos"].append(acesso)
    save_db(db)
    audit_log("ACESSO", "equipamento", equipamento_id, usuario_id, {"tipo": tipo})
    return acesso

def listar_acessos(filtro_usuario: Optional[int] = None) -> List[dict]:
    db = load_db()
    acessos = db["acessos"]
    if filtro_usuario:
        acessos = [a for a in acessos if a["usuario_id"] == filtro_usuario]
    return sorted(acessos, key=lambda x: x["timestamp"], reverse=True)

# ======================== AUDITORIA ========================

def listar_auditoria(limite: int = 100) -> List[dict]:
    db = load_db()
    return sorted(db["auditoria"], key=lambda x: x["timestamp"], reverse=True)[:limite]
