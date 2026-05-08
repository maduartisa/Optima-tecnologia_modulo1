# models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Usuario(BaseModel):
    id: Optional[int] = None
    nome: str = Field(..., min_length=1, max_length=100)
    perfil: str = Field(..., min_length=1, max_length=50)
    credenciais: Dict[str, Any] = Field(...)
    ativo: bool = True
    created_at: Optional[str] = None
    permissoes: List[str] = Field(default_factory=list)

class Modulo(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str = Field(..., min_length=1, max_length=500)
    versao: str = Field(..., min_length=1, max_length=20)
    permissoes: List[str] = Field(default_factory=list)
    habilitado: bool = True

class LogEntry(BaseModel):
    evento: str
    entidade: str
    entidade_id: Any
    usuario_responsavel: str = "system"
    detalhe: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str