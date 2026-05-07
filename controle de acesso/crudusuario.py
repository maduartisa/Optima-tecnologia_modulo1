import streamlit as st
import json
import os
from uuid import uuid4

ARQUIVO = "usuarios.json"

# ==============================
# VALIDADOR DE DATA
# ==============================
def validar_data(data):
    partes = data.split("/")
    if len(partes) == 3:
        dia, mes, ano = partes
        if dia.isdigit() and mes.isdigit() and ano.isdigit():
            return True
    return False


# ==============================
# MODELO DE CLASSE
# ==============================
class Usuario:
    def __init__(self, id, nome, cpf, data_nasc, naturalidade, nacionalidade, nome_social,
                 sexo, endereco, cep, cidade, estado,
                 telefone, tipo_usuario, email, uf):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.data_nasc = data_nasc
        self.naturalidade = naturalidade
        self.nacionalidade = nacionalidade
        self.nome_social = nome_social
        self.sexo = sexo
        self.endereco = endereco
        self.cep = cep
        self.cidade = cidade
        self.estado = estado
        self.telefone = telefone
        self.tipo_usuario = tipo_usuario
        self.email = email
        self.uf = uf

    def to_dict(self):
        return self.__dict__


# ==============================
# FUNÇÕES JSON
# ==============================
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# ==============================
# CRUD
# ==============================
def listar_usuarios():
    return carregar_dados()

def atualizar_usuario(id, novos_dados):
    dados = carregar_dados()
    for u in dados:
        if u["id"] == id:
            u.update(novos_dados)
    salvar_dados(dados)

def deletar_usuario(id):
    dados = carregar_dados()
    dados = [u for u in dados if u["id"] != id]
    salvar_dados(dados)


# ==============================
# INTERFACE
# ==============================
st.set_page_config(layout="wide", page_title="Cadastro de Usuários")

st.title("📋 Sistema de Cadastro de Usuários")

menu = st.sidebar.selectbox("Navegação", ["Criar", "Listar", "Atualizar", "Excluir"])


# ==============================
# CREATE
# ==============================
if menu == "Criar":
    st.subheader("➕ Cadastro Inteligente de Usuário")

    col1, col2 = st.columns(2)

    with st.form("form_usuario"):

        with col1:
            st.markdown("### 👤 Dados Pessoais")
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF")

            # ✅ SEM LIMITE DE ANO
            data_nasc = st.text_input("Data de Nascimento (DD/MM/AAAA)")

            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            telefone = st.text_input("Telefone")
            nome_social = st.text_input("Nome Social")
            email = st.text_input("E-mail")

        with col2:
            st.markdown("### 📍 Endereço")
            endereco = st.text_input("Endereço")
            cep = st.text_input("CEP")
            cidade = st.text_input("Cidade")
            estado = st.text_input("Estado")
            nacionalidade = st.text_input("Nacionalidade")
            naturalidade = st.text_input("Naturalidade")
            uf = st.text_input("UF")
            
                st.markdown("---")

        # =========================
        # TIPO DE USUÁRIO
        # =========================
        tipo_usuario = st.selectbox("Tipo de Usuário", [
            "Administrador", "Funcionário", "Visitante",
            "Motorista", "Lojista", "Fornecedor"
        ])

        dados_especificos = {}

        st.markdown("### ⚙️ Dados Específicos")

        # =========================
        # ADMIN
        # =========================
        if tipo_usuario == "Administrador":
            colA, colB = st.columns(2)
            with colA:
                dados_especificos["cnpj"] = st.text_input("CNPJ")
                dados_especificos["matricula"] = st.text_input("Matrícula")
                dados_especificos["cargo"] = st.text_input("Cargo")
            with colB:
                dados_especificos["funcao"] = st.text_input("Função")
                dados_especificos["horario_entrada"] = str(st.time_input("Entrada"))
                dados_especificos["horario_saida"] = str(st.time_input("Saída"))

        # =========================
        # FUNCIONÁRIO
        # =========================
        elif tipo_usuario == "Funcionário":
            colA, colB = st.columns(2)
            with colA:
                dados_especificos["departamento"] = st.text_input("Departamento")
                dados_especificos["matricula"] = st.text_input("Matrícula")
            with colB:
                dados_especificos["cargo"] = st.text_input("Cargo")
                dados_especificos["data_admissao"] = st.text_input("Data Admissão (DD/MM/AAAA)")

        # =========================
        # VISITANTE
        # =========================
        elif tipo_usuario == "Visitante":
            dados_especificos["motivo"] = st.text_input("Motivo da visita")
            dados_especificos["data"] = st.text_input("Data da visita (DD/MM/AAAA)")
            dados_especificos["entrada"] = str(st.time_input("Hora Entrada"))
            dados_especificos["saida"] = str(st.time_input("Hora Saída"))

        # =========================
        # MOTORISTA
        # =========================
        elif tipo_usuario == "Motorista":
            dados_especificos["cnh"] = st.text_input("CNH")
            dados_especificos["categoria"] = st.text_input("Categoria")
            dados_especificos["validade"] = st.text_input("Validade CNH (DD/MM/AAAA)")

        # =========================
        # LOJISTA
        # =========================
        elif tipo_usuario == "Lojista":
            colA, colB = st.columns(2)
            with colA:
                dados_especificos["cnpj"] = st.text_input("CNPJ")
                dados_especificos["nome_loja"] = st.text_input("Nome da Loja")
                dados_especificos["segmento"] = st.text_input("Segmento")
            with colB:
                dados_especificos["num_funcionarios"] = st.number_input("Nº Funcionários")
                dados_especificos["horario_abertura"] = str(st.time_input("Abertura"))
                dados_especificos["horario_fechamento"] = str(st.time_input("Fechamento"))

        # =========================
        # FORNECEDOR
        # =========================
        elif tipo_usuario == "Fornecedor":
            dados_especificos["empresa"] = st.text_input("Empresa")
            dados_especificos["segmento"] = st.text_input("Segmento")
            dados_especificos["cargo"] = st.text_input("Cargo")

        st.markdown("---")

        submitted = st.form_submit_button("💾 Salvar")

        if submitted:
            if not validar_data(data_nasc):
                st.error("❌ Data inválida. Use DD/MM/AAAA.")
            else:
                usuario = Usuario(
                    str(uuid4()), nome, cpf, data_nasc,
                    naturalidade, nacionalidade,
                    nome_social, sexo, endereco, cep, cidade, estado,
                    telefone, tipo_usuario, email, uf
                )

                user_dict = usuario.to_dict()
                user_dict["dados_especificos"] = dados_especificos

                dados = carregar_dados()
                dados.append(user_dict)
                salvar_dados(dados)

                st.success("✅ Usuário cadastrado com sucesso!")


# ==============================
# LISTAR
# ==============================
elif menu == "Listar":
    st.subheader("📄 Lista de Usuários")

    usuarios = listar_usuarios()

    if usuarios:
        for u in usuarios:
            with st.expander(f"{u['nome']} - {u['cpf']}"):
                st.json(u)
    else:
        st.info("Nenhum usuário cadastrado.")


# ==============================
# UPDATE
# ==============================
elif menu == "Atualizar":
    st.subheader("✏️ Atualizar Usuário")

    usuarios = listar_usuarios()
    ids = {u["nome"]: u["id"] for u in usuarios}

    if ids:
        nome_sel = st.selectbox("Selecione o usuário", list(ids.keys()))
        id_sel = ids[nome_sel]

        novo_email = st.text_input("Novo E-mail")
        novo_telefone = st.text_input("Novo Telefone")

        if st.button("Atualizar"):
            atualizar_usuario(id_sel, {
                "email": novo_email,
                "telefone": novo_telefone
            })
            st.success("✅ Atualizado com sucesso!")
    else:
        st.warning("Nenhum usuário disponível.")


# ==============================
# DELETE
# ==============================
elif menu == "Excluir":
    st.subheader("🗑️ Excluir Usuário")

    usuarios = listar_usuarios()
    ids = {u["nome"]: u["id"] for u in usuarios}

    if ids:
        nome_sel = st.selectbox("Selecione o usuário", list(ids.keys()))
        id_sel = ids[nome_sel]

        if st.button("Excluir"):
            deletar_usuario(id_sel)
            st.success("✅ Usuário excluído!")
    else:
        st.warning("Nenhum usuário disponível.")