# app_streamlit.py
import streamlit as st
import json
from datetime import datetime
from db import load_db, save_db, audit, next_int_id
from models import Usuario, Modulo, LogEntry

st.set_page_config(page_title="Sistema cnaK - Controle de Acesso", layout="wide")

# Funções auxiliares
def carregar_usuarios():
    db = load_db()
    return db["usuarios"]

def salvar_usuarios(usuarios):
    db = load_db()
    db["usuarios"] = usuarios
    save_db(db)

def carregar_modulos():
    db = load_db()
    return db["modulos"]

def salvar_modulos(modulos):
    db = load_db()
    db["modulos"] = modulos
    save_db(db)

def carregar_logs():
    db = load_db()
    return db["logs"]

# Páginas
def pagina_usuarios():
    st.header("Gerenciamento de Usuários")

    usuarios = carregar_usuarios()

    # Listar usuários
    st.subheader("Usuários Cadastrados")
    if usuarios:
        for usuario in usuarios:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
            with col1:
                st.write(f"ID: {usuario['id']}")
            with col2:
                st.write(f"Nome: {usuario['nome']}")
            with col3:
                st.write(f"Perfil: {usuario['perfil']}")
            with col4:
                st.write(f"Ativo: {'Sim' if usuario.get('ativo', True) else 'Não'}")
            with col5:
                if st.button(f"Editar {usuario['id']}", key=f"edit_{usuario['id']}"):
                    st.session_state['edit_user'] = usuario
                    st.rerun()
                if st.button(f"Deletar {usuario['id']}", key=f"del_{usuario['id']}"):
                    usuarios.remove(usuario)
                    salvar_usuarios(usuarios)
                    audit("DELETE", "usuario", usuario['id'], "admin")
                    st.success("Usuário deletado!")
                    st.rerun()
    else:
        st.write("Nenhum usuário cadastrado.")

    # Formulário para adicionar/editar usuário
    st.subheader("Adicionar/Editar Usuário")
    if 'edit_user' in st.session_state:
        usuario = st.session_state['edit_user']
        nome = st.text_input("Nome", value=usuario['nome'])
        perfil = st.text_input("Perfil", value=usuario['perfil'])
        credenciais_str = st.text_area("Credenciais (JSON)", value=json.dumps(usuario['credenciais'], indent=2))
        ativo = st.checkbox("Ativo", value=usuario.get('ativo', True))
        permissoes_str = st.text_area("Permissões (uma por linha)", value="\n".join(usuario.get('permissoes', [])))
        if st.button("Salvar Edição"):
            try:
                credenciais = json.loads(credenciais_str)
                permissoes = [p.strip() for p in permissoes_str.split('\n') if p.strip()]
                usuario.update({
                    'nome': nome,
                    'perfil': perfil,
                    'credenciais': credenciais,
                    'ativo': ativo,
                    'permissoes': permissoes
                })
                salvar_usuarios(usuarios)
                audit("UPDATE", "usuario", usuario['id'], "admin", {"nome": nome})
                st.success("Usuário atualizado!")
                del st.session_state['edit_user']
                st.rerun()
            except json.JSONDecodeError:
                st.error("Credenciais devem ser um JSON válido.")
    else:
        nome = st.text_input("Nome")
        perfil = st.text_input("Perfil")
        credenciais_str = st.text_area("Credenciais (JSON)", value='{"cpf": "12345678900"}')
        ativo = st.checkbox("Ativo", value=True)
        permissoes_str = st.text_area("Permissões (uma por linha)")
        if st.button("Adicionar Usuário"):
            try:
                credenciais = json.loads(credenciais_str)
                permissoes = [p.strip() for p in permissoes_str.split('\n') if p.strip()]
                novo_id = next_int_id(usuarios)
                usuario = {
                    'id': novo_id,
                    'nome': nome,
                    'perfil': perfil,
                    'credenciais': credenciais,
                    'ativo': ativo,
                    'created_at': datetime.utcnow().isoformat() + "Z",
                    'permissoes': permissoes
                }
                usuarios.append(usuario)
                salvar_usuarios(usuarios)
                audit("CREATE", "usuario", novo_id, "admin", {"nome": nome})
                st.success("Usuário adicionado!")
                st.rerun()
            except json.JSONDecodeError:
                st.error("Credenciais devem ser um JSON válido.")

def pagina_acessos():
    st.header("Controle de Acessos")

    usuarios = carregar_usuarios()
    modulos = carregar_modulos()

    # Autorizações
    st.subheader("Autorizações de Acesso")
    if usuarios:
        usuario_selecionado = st.selectbox("Selecionar Usuário", [u['nome'] for u in usuarios])
        usuario = next(u for u in usuarios if u['nome'] == usuario_selecionado)
        st.write(f"Permissões atuais: {', '.join(usuario.get('permissoes', []))}")

        novas_permissoes = st.multiselect("Editar Permissões", [m['id'] for m in modulos], default=usuario.get('permissoes', []))
        if st.button("Salvar Permissões"):
            usuario['permissoes'] = novas_permissoes
            salvar_usuarios(usuarios)
            audit("UPDATE_PERMISSIONS", "usuario", usuario['id'], "admin", {"permissoes": novas_permissoes})
            st.success("Permissões atualizadas!")
    else:
        st.write("Nenhum usuário cadastrado.")

    # Logs de acessos (simulado)
    st.subheader("Logs de Acessos")
    logs = carregar_logs()
    if logs:
        for log in logs[-10:]:  # Últimos 10
            st.write(f"{log['timestamp']} - {log['evento']} - {log['entidade']} ID: {log['entidade_id']} - {log['usuario_responsavel']}")
    else:
        st.write("Nenhum log encontrado.")

def pagina_equipamentos():
    st.header("Gerenciamento de Equipamentos")

    modulos = carregar_modulos()

    # Listar módulos
    st.subheader("Equipamentos/Equipamentos Cadastrados")
    if modulos:
        for modulo in modulos:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
            with col1:
                st.write(f"ID: {modulo['id']}")
            with col2:
                st.write(f"Nome: {modulo['nome']}")
            with col3:
                st.write(f"Versão: {modulo['versao']}")
            with col4:
                st.write(f"Habilitado: {'Sim' if modulo.get('habilitado', True) else 'Não'}")
            with col5:
                if st.button(f"Deletar {modulo['id']}", key=f"del_mod_{modulo['id']}"):
                    modulos.remove(modulo)
                    salvar_modulos(modulos)
                    audit("DELETE", "modulo", modulo['id'], "admin")
                    st.success("Equipamento deletado!")
                    st.rerun()
    else:
        st.write("Nenhum equipamento cadastrado.")

    # Formulário para adicionar equipamento
    st.subheader("Adicionar Equipamento")
    id_mod = st.text_input("ID do Equipamento")
    nome = st.text_input("Nome")
    descricao = st.text_area("Descrição")
    versao = st.text_input("Versão")
    permissoes_str = st.text_area("Permissões (uma por linha)")
    habilitado = st.checkbox("Habilitado", value=True)
    if st.button("Adicionar Equipamento"):
        permissoes = [p.strip() for p in permissoes_str.split('\n') if p.strip()]
        modulo = {
            'id': id_mod,
            'nome': nome,
            'descricao': descricao,
            'versao': versao,
            'permissoes': permissoes,
            'habilitado': habilitado
        }
        modulos.append(modulo)
        salvar_modulos(modulos)
        audit("CREATE", "modulo", id_mod, "admin", {"nome": nome})
        st.success("Equipamento adicionado!")
        st.rerun()

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Usuários", "Acessos", "Equipamentos"])

if menu == "Usuários":
    pagina_usuarios()
elif menu == "Acessos":
    pagina_acessos()
elif menu == "Equipamentos":
    pagina_equipamentos()

# Rodapé
st.sidebar.markdown("---")
st.sidebar.write("Sistema cnaK - Controle de Acesso")