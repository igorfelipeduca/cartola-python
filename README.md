# Trabalho Banco de Dados - Futebol App

Sistema de gerenciamento de times de futebol com usuários, jogadores e times oficiais.

## Estrutura do Banco de Dados

O banco contém as seguintes tabelas:

- **USUARIO**: Cadastro de usuários do sistema
- **TIME_OFICIAL**: Times oficiais de futebol
- **JOGADOR**: Jogadores vinculados aos times oficiais
- **TIME_USUARIO**: Times criados pelos usuários
- **TIME_USUARIO_JOGADOR**: Relação entre times de usuário e jogadores

## Como usar

### 1. Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar o banco de dados (primeira vez)

Execute este comando apenas na primeira vez para criar as tabelas e inserir dados iniciais:

```bash
python setup_database.py
```

Este script irá:
- Criar o banco de dados `futebol_app`
- Criar todas as tabelas necessárias
- Inserir dados de teste
- Executar 5 queries de leitura

### 3. Executar o aplicativo interativo

Para usar o sistema completo com interface de terminal:

```bash
python app.py
```

## Funcionalidades do Aplicativo

O aplicativo oferece um menu interativo com as seguintes opções:

### Menu de Cadastros
1. **Cadastrar Usuário** - Registrar novos usuários no sistema
2. **Cadastrar Time Oficial** - Adicionar times oficiais de futebol
3. **Cadastrar Jogador** - Registrar jogadores (com ou sem time)
4. **Criar Time de Usuário** - Criar times personalizados para usuários
5. **Adicionar Jogador ao Time de Usuário** - Montar os times dos usuários

### Menu de Consultas
1. **Listar Usuários** - Ver todos os usuários cadastrados
2. **Listar Times Oficiais** - Ver todos os times oficiais
3. **Listar Jogadores** - Ver todos os jogadores cadastrados
4. **Listar Times de Usuário** - Ver times de usuários e seus jogadores
5. **Consultas Avançadas**:
   - Jogadores por posição em cada time oficial
   - Jogadores sem time oficial
   - Jogadores do time preferido nos times de usuário

## Arquivos do Projeto

- `script.sql` - Script SQL original com a estrutura do banco
- `setup_database.py` - Script para inicializar o banco com dados de teste
- `app.py` - Aplicativo interativo de terminal
- `requirements.txt` - Dependências do projeto

## Conexão com o Banco

O sistema está configurado para conectar ao banco MySQL hospedado no Railway. A URL de conexão está definida nos arquivos `setup_database.py` e `app.py`.
