# app_sistema_admin.py
import streamlit as st
from datetime import datetime
from sistema_admin import (
    criar_administrador,
    autenticar_admin,
    listar_administradores,
    criar_usuario,
    autenticar_usuario,
    obter_usuario,
    atualizar_usuario,
    deletar_usuario,
    listar_usuarios,
    criar_equipamento,
    obter_equipamento,
    atualizar_equipamento,
    deletar_equipamento,
    listar_equipamentos,
    registrar_acesso,
    listar_acessos,
    listar_auditoria,
    load_db,
    audit_log
)

st.set_page_config(page_title="cnaK - Sistema de Controle Administrativo", layout="wide")

# ======================== INICIALIZAÇÃO DE ESTADO ========================

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = None
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# ======================== PÁGINA DE LOGIN ========================

def pagina_login():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.title("🔐 cnaK Admin")
        st.write("Sistema de Controle Administrativo")
        st.divider()
        
        tab1, tab2 = st.tabs(["Login Admin", "Login Usuário"])
        
        with tab1:
            st.subheader("Autenticação de Administrador")
            email_admin = st.text_input("Email", key="email_admin")
            senha_admin = st.text_input("Senha", type="password", key="senha_admin")
            if st.button("Entrar como Admin"):
                admin = autenticar_admin(email_admin, senha_admin)
                if admin:
                    st.session_state.admin_logado = admin
                    audit_log("LOGIN", "administrador", admin["id"], admin["id"])
                    st.success(f"Bem-vindo, {admin['nome']}!")
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos")
        
        with tab2:
            st.subheader("Autenticação de Usuário")
            email_user = st.text_input("Email", key="email_user")
            senha_user = st.text_input("Senha", type="password", key="senha_user")
            if st.button("Entrar como Usuário"):
                usuario = autenticar_usuario(email_user, senha_user)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    audit_log("LOGIN", "usuario", usuario["id"], usuario["id"])
                    st.success(f"Bem-vindo, {usuario['nome']}!")
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos")
    
    with col2:
        st.info("""
        ### Sistema cnaK
        
        **Funcionalidades:**
        - Gestão de Administradores
        - Controle de Usuários
        - Cadastro de Equipamentos
        - Autorização de Acessos
        - Auditoria Completa
        
        **Perfis Disponíveis:**
        - Admin Super (gerenciamento total)
        - Admin Moderador
        - Usuário Operador
        - Usuário Supervisor
        """)

# ======================== PAINEL ADMINISTRADOR ========================

def painel_admin():
    st.title("🏢 Painel Administrativo")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.admin_logado = None
        st.rerun()
    
    admin = st.session_state.admin_logado
    st.write(f"Conectado como: **{admin['nome']}** ({admin['perfil']})")
    st.divider()
    
    menu = st.sidebar.selectbox("Menu", [
        "Dashboard",
        "Administradores",
        "Usuários",
        "Equipamentos",
        "Acessos",
        "Auditoria"
    ])
    
    if menu == "Dashboard":
        pagina_dashboard()
    elif menu == "Administradores":
        pagina_administradores()
    elif menu == "Usuários":
        pagina_usuarios_admin()
    elif menu == "Equipamentos":
        pagina_equipamentos_admin()
    elif menu == "Acessos":
        pagina_acessos_admin()
    elif menu == "Auditoria":
        pagina_auditoria()

def pagina_dashboard():
    st.subheader("📊 Dashboard")
    
    usuarios = listar_usuarios()
    equipamentos = listar_equipamentos()
    acessos = listar_acessos()
    admins = listar_administradores()
    auditoria = listar_auditoria(10)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Administradores", len(admins))
    with col2:
        st.metric("Usuários", len(usuarios))
    with col3:
        st.metric("Equipamentos", len(equipamentos))
    with col4:
        st.metric("Acessos (hoje)", len([a for a in acessos if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")).date() == datetime.utcnow().date()]))
    
    st.divider()
    st.subheader("📋 Últimas Atividades")
    for log in auditoria[:5]:
        st.write(f"**{log['evento']}** - {log['entidade']} #{log['entidade_id']} - {log['timestamp']}")

def pagina_administradores():
    st.subheader("👨‍💼 Gerenciamento de Administradores")
    
    tab1, tab2 = st.tabs(["Listar", "Criar Novo"])
    
    with tab1:
        admins = listar_administradores()
        if admins:
            for admin in admins:
                with st.expander(f"{admin['nome']} ({admin['perfil']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email**: {admin['email']}")
                        st.write(f"**ID**: {admin['id']}")
                    with col2:
                        st.write(f"**Perfil**: {admin['perfil']}")
                        st.write(f"**Ativo**: {'Sim' if admin['ativo'] else 'Não'}")
        else:
            st.write("Nenhum administrador cadastrado.")
    
    with tab2:
        st.write("Criar novo administrador")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox("Perfil", ["super", "moderador"])
        if st.button("Criar Administrador"):
            if nome and email and senha:
                admin = criar_administrador(nome, email, senha, perfil)
                st.success(f"Administrador criado: {admin['nome']}")
                st.rerun()
            else:
                st.error("Preencha todos os campos")

def pagina_usuarios_admin():
    st.subheader("👥 Gerenciamento de Usuários")
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Criar Novo", "Editar"])
    
    with tab1:
        usuarios = listar_usuarios()
        if usuarios:
            for usuario in usuarios:
                with st.expander(f"{usuario['nome']} (ID: {usuario['id']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Email**: {usuario['email']}")
                        st.write(f"**Perfil**: {usuario['perfil']}")
                    with col2:
                        st.write(f"**Ativo**: {'Sim' if usuario['ativo'] else 'Não'}")
                        st.write(f"**Criado**: {usuario['created_at']}")
                    with col3:
                        if st.button(f"Deletar {usuario['id']}", key=f"del_{usuario['id']}"):
                            deletar_usuario(usuario['id'])
                            st.success("Usuário deletado!")
                            st.rerun()
        else:
            st.write("Nenhum usuário cadastrado.")
    
    with tab2:
        st.write("Criar novo usuário")
        nome = st.text_input("Nome", key="new_user_name")
        email = st.text_input("Email", key="new_user_email")
        senha = st.text_input("Senha", type="password", key="new_user_senha")
        perfil = st.selectbox("Perfil", ["operador", "supervisor"], key="new_user_perfil")
        if st.button("Criar Usuário"):
            if nome and email and senha:
                usuario = criar_usuario(nome, email, senha, perfil)
                st.success(f"Usuário criado: {usuario['nome']} (ID: {usuario['id']})")
                st.rerun()
            else:
                st.error("Preencha todos os campos")
    
    with tab3:
        st.write("Editar usuário")
        usuarios = listar_usuarios()
        if usuarios:
            usuario_selecionado = st.selectbox("Selecionar usuário", [f"{u['nome']} (ID: {u['id']})" for u in usuarios])
            usuario_id = int(usuario_selecionado.split("(ID: ")[-1].rstrip(")"))
            usuario = obter_usuario(usuario_id)
            
            nome = st.text_input("Nome", value=usuario['nome'])
            email = st.text_input("Email", value=usuario['email'])
            perfil = st.selectbox("Perfil", ["operador", "supervisor"], index=0 if usuario['perfil'] == "operador" else 1)
            ativo = st.checkbox("Ativo", value=usuario['ativo'])
            
            if st.button("Salvar Alterações"):
                atualizar_usuario(usuario_id, {
                    "nome": nome,
                    "email": email,
                    "perfil": perfil,
                    "ativo": ativo
                })
                st.success("Usuário atualizado!")
                st.rerun()
        else:
            st.write("Nenhum usuário disponível")

def pagina_equipamentos_admin():
    st.subheader("🖥️ Gerenciamento de Equipamentos")
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Criar Novo", "Editar"])
    
    with tab1:
        equipamentos = listar_equipamentos()
        if equipamentos:
            for eq in equipamentos:
                with st.expander(f"{eq['nome']} (ID: {eq['id']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tipo**: {eq['tipo']}")
                        st.write(f"**Local**: {eq['local']}")
                    with col2:
                        st.write(f"**Status**: {eq['status']}")
                        st.write(f"**Responsável ID**: {eq['responsavel_id']}")
                    with col3:
                        st.write(f"**Criado**: {eq['created_at']}")
                        if st.button(f"Deletar {eq['id']}", key=f"del_eq_{eq['id']}"):
                            deletar_equipamento(eq['id'])
                            st.success("Equipamento deletado!")
                            st.rerun()
        else:
            st.write("Nenhum equipamento cadastrado.")
    
    with tab2:
        st.write("Criar novo equipamento")
        nome = st.text_input("Nome do Equipamento", key="new_eq_name")
        tipo = st.text_input("Tipo", key="new_eq_tipo")
        local = st.text_input("Local", key="new_eq_local")
        usuarios = listar_usuarios()
        responsavel = st.selectbox("Responsável", [f"{u['nome']} (ID: {u['id']})" for u in usuarios] if usuarios else [])
        responsavel_id = int(responsavel.split("(ID: ")[-1].rstrip(")")) if responsavel else None
        
        if st.button("Criar Equipamento"):
            if nome and tipo and local:
                equipamento = criar_equipamento(nome, tipo, local, responsavel_id)
                st.success(f"Equipamento criado: {equipamento['nome']} (ID: {equipamento['id']})")
                st.rerun()
            else:
                st.error("Preencha todos os campos")
    
    with tab3:
        st.write("Editar equipamento")
        equipamentos = listar_equipamentos()
        if equipamentos:
            eq_selecionado = st.selectbox("Selecionar equipamento", [f"{e['nome']} (ID: {e['id']})" for e in equipamentos])
            eq_id = int(eq_selecionado.split("(ID: ")[-1].rstrip(")"))
            equipamento = obter_equipamento(eq_id)
            
            nome = st.text_input("Nome", value=equipamento['nome'])
            tipo = st.text_input("Tipo", value=equipamento['tipo'])
            local = st.text_input("Local", value=equipamento['local'])
            status = st.selectbox("Status", ["ativo", "inativo", "manutenção"], index=["ativo", "inativo", "manutenção"].index(equipamento['status']))
            
            if st.button("Salvar Alterações"):
                atualizar_equipamento(eq_id, {
                    "nome": nome,
                    "tipo": tipo,
                    "local": local,
                    "status": status
                })
                st.success("Equipamento atualizado!")
                st.rerun()
        else:
            st.write("Nenhum equipamento disponível")

def pagina_acessos_admin():
    st.subheader("🔑 Controle de Acessos")
    
    tab1, tab2 = st.tabs(["Registrar Acesso", "Histórico"])
    
    with tab1:
        usuarios = listar_usuarios()
        equipamentos = listar_equipamentos()
        
        if usuarios and equipamentos:
            usuario_opt = st.selectbox("Selecionar Usuário", [f"{u['nome']} (ID: {u['id']})" for u in usuarios])
            usuario_id = int(usuario_opt.split("(ID: ")[-1].rstrip(")"))
            
            eq_opt = st.selectbox("Selecionar Equipamento", [f"{e['nome']} (ID: {e['id']})" for e in equipamentos])
            eq_id = int(eq_opt.split("(ID: ")[-1].rstrip(")"))
            
            tipo_acesso = st.selectbox("Tipo de Acesso", ["acesso", "saída", "tentativa_negada"])
            
            if st.button("Registrar Acesso"):
                acesso = registrar_acesso(usuario_id, eq_id, tipo_acesso)
                st.success(f"Acesso registrado! ID: {acesso['id']}")
                st.rerun()
        else:
            st.warning("Cadastre usuários e equipamentos primeiro")
    
    with tab2:
        acessos = listar_acessos()
        if acessos:
            st.write(f"Total de acessos: {len(acessos)}")
            for acesso in acessos[:20]:
                usuario = obter_usuario(acesso['usuario_id'])
                equipamento = obter_equipamento(acesso['equipamento_id'])
                usuario_nome = usuario['nome'] if usuario else "Desconhecido"
                eq_nome = equipamento['nome'] if equipamento else "Desconhecido"
                st.write(f"**{acesso['timestamp']}** - {usuario_nome} → {eq_nome} ({acesso['tipo']})")
        else:
            st.write("Nenhum acesso registrado")

def pagina_auditoria():
    st.subheader("📜 Log de Auditoria")
    
    logs = listar_auditoria(500)
    
    if logs:
        st.write(f"Total de eventos: {len(logs)}")
        
        filtro_evento = st.selectbox("Filtrar por evento", ["Todos"] + list(set([l['evento'] for l in logs])))
        
        if filtro_evento != "Todos":
            logs = [l for l in logs if l['evento'] == filtro_evento]
        
        for log in logs[:50]:
            status_color = {
                "CREATE": "🟢",
                "UPDATE": "🟡",
                "DELETE": "🔴",
                "LOGIN": "🔵",
                "ACESSO": "🟣"
            }.get(log['evento'], "⚪")
            
            st.write(f"{status_color} **{log['evento']}** - {log['entidade']} #{log['entidade_id']} - {log['timestamp']}")
    else:
        st.write("Nenhum evento registrado")

# ======================== PAINEL USUÁRIO ========================

def painel_usuario():
    st.title("📱 Painel do Usuário")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.usuario_logado = None
        st.rerun()
    
    usuario = st.session_state.usuario_logado
    st.write(f"Conectado como: **{usuario['nome']}** ({usuario['perfil']})")
    st.divider()
    
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Meus Acessos", "Equipamentos"])
    
    if menu == "Dashboard":
        st.subheader("📊 Dashboard")
        acessos = listar_acessos(usuario['id'])
        st.metric("Meus Acessos", len(acessos))
        
        if acessos:
            st.write("Últimos acessos:")
            for acesso in acessos[:5]:
                eq = obter_equipamento(acesso['equipamento_id'])
                eq_nome = eq['nome'] if eq else "Desconhecido"
                st.write(f"- {acesso['timestamp']} → {eq_nome}")
    
    elif menu == "Meus Acessos":
        st.subheader("🔑 Meus Acessos")
        acessos = listar_acessos(usuario['id'])
        if acessos:
            for acesso in acessos:
                eq = obter_equipamento(acesso['equipamento_id'])
                eq_nome = eq['nome'] if eq else "Desconhecido"
                st.write(f"**{acesso['timestamp']}** - {eq_nome} ({acesso['tipo']})")
        else:
            st.write("Você ainda não tem acessos registrados")
    
    elif menu == "Equipamentos":
        st.subheader("🖥️ Equipamentos Disponíveis")
        equipamentos = listar_equipamentos()
        if equipamentos:
            for eq in equipamentos:
                if eq['status'] == 'ativo':
                    st.write(f"**{eq['nome']}** - {eq['tipo']} ({eq['local']})")
        else:
            st.write("Nenhum equipamento disponível")

# ======================== EXECUÇÃO PRINCIPAL ========================

if st.session_state.admin_logado:
    painel_admin()
elif st.session_state.usuario_logado:
    painel_usuario()
else:
    pagina_login()

st.sidebar.markdown("---")
st.sidebar.write("cnaK v1.0 - Sistema de Controle Administrativo")