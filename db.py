# db.py
import json
import os
from datetime import datetime
from threading import Lock
from typing import Any, Dict

DB_FILE = "cnaK_db.json"
_lock = Lock()

DEFAULT_DB = {
    "usuarios": [],      # cada usuário: id(int), nome, perfil, credenciais(dict), ativo(bool), created_at, permissoes(list)
    "modulos": [],       # cada módulo: id(str), nome, descricao, versao, permissoes(list[str]), habilitado(bool)
    "logs": []           # logs de auditoria
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

def audit(evento: str, entidade: str, entidade_id, usuario_responsavel: str = "system", detalhe: dict = None):
    db = load_db()
    entry = {
        "evento": evento,
        "entidade": entidade,
        "entidade_id": entidade_id,
        "usuario_responsavel": usuario_responsavel,
        "detalhe": detalhe or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    db["logs"].append(entry)
    save_db(db)
    return entry

def next_int_id(collection: list) -> int:
    ints = [item["id"] for item in collection if isinstance(item.get("id"), int)]
    return (max(ints) + 1) if ints else 1