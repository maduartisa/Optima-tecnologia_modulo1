# Sistema cnaK - Controle de Acesso

Este é um módulo de controle de usuários, acessos e equipamentos para o sistema cnaK, implementado com Streamlit para interface web e armazenamento em JSON.

## Funcionalidades

- **Gerenciamento de Usuários**: CRUD completo (Criar, Ler, Atualizar, Deletar) com validação Pydantic
- **Controle de Acessos**: Autorizações de acesso por usuário, logs de auditoria
- **Gerenciamento de Equipamentos**: Cadastro e controle de módulos/equipamentos

## Estrutura do Projeto

- `db.py`: Helpers de persistência JSON e auditoria
- `models.py`: Schemas Pydantic para validação
- `app_streamlit.py`: Interface web Streamlit
- `requirements.txt`: Dependências Python
- `cnaK_db.json`: Banco de dados JSON (criado automaticamente)

## Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:
   ```bash
   streamlit run app_streamlit.py
   ```

3. Acesse no navegador: http://localhost:8501

## Uso

- **Usuários**: Adicione, edite ou remova usuários com credenciais, perfis e permissões
- **Acessos**: Gerencie autorizações de acesso e visualize logs de auditoria
- **Equipamentos**: Cadastre módulos/equipamentos com permissões associadas

Todos os dados são armazenados em `cnaK_db.json` e logs de auditoria são mantidos automaticamente.