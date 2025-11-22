# Trabalho Banco de Dados - Futebol App

Sistema de gerenciamento de times de futebol com usuários, jogadores e times oficiais.

## Estrutura do Banco de Dados

O banco MongoDB contém as seguintes coleções:

- **usuario**: Cadastro de usuários do sistema
- **time_oficial**: Times oficiais de futebol
- **jogador**: Jogadores vinculados aos times oficiais
- **time_usuario**: Times criados pelos usuários
- **time_usuario_jogador**: Relação entre times de usuário e jogadores

## Como usar

### 1. Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure sua conexão MongoDB:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure a variável `MONGODB_URI`:

```
MONGODB_URI=mongodb://username:password@host:port/database
# Ou para MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
```

### 3. Configurar o banco de dados (primeira vez)

Execute este comando apenas na primeira vez para criar as coleções e inserir dados iniciais:

```bash
python setup_database.py
```

Este script irá:
- Criar o banco de dados `futebol_app`
- Criar todas as coleções necessárias
- Criar índices únicos para email e sigla
- Inserir dados de teste
- Executar 5 queries de leitura

### 4. Executar o aplicativo interativo

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

- `script.sql` - Script SQL original (legado - MySQL)
- `script.js` - Script MongoDB Shell com a estrutura do banco
- `setup_database.py` - Script Python para inicializar o banco com dados de teste
- `app.py` - Aplicativo interativo de terminal
- `reset.py` - Script para limpar todas as coleções do banco
- `requirements.txt` - Dependências do projeto
- `.env.example` - Exemplo de configuração de variáveis de ambiente

## Conexão com o Banco

O sistema utiliza MongoDB. Configure a URI de conexão no arquivo `.env` usando a variável `MONGODB_URI`.

Exemplos:
- MongoDB local: `mongodb://localhost:27017/futebol_app`
- MongoDB Atlas: `mongodb+srv://user:pass@cluster.mongodb.net/futebol_app`
- MongoDB hospedado: `mongodb://user:pass@host:port/futebol_app`
