# Exemplo de Uso do Aplicativo

Este guia mostra como usar o aplicativo passo a passo.

## Iniciando o Aplicativo

```bash
source venv/bin/activate
python app.py
```

## Fluxo de Exemplo

### 1. Cadastrar um Novo Usuário

```
Menu Principal > 1 (Cadastros) > 1 (Cadastrar Usuário)
```

Exemplo de dados:
```
Nome completo: João Silva
Email: joao@example.com
Senha: senha123
Sexo: 1 (Masculino)
Telefone: 11-98765-4321
Data de nascimento: 1995-05-15
Time preferido: Flamengo
```

### 2. Cadastrar um Time Oficial

```
Menu Principal > 1 (Cadastros) > 2 (Cadastrar Time Oficial)
```

Exemplo de dados:
```
Nome do time: Flamengo
Sigla do time: FLA
```

### 3. Cadastrar Jogadores

```
Menu Principal > 1 (Cadastros) > 3 (Cadastrar Jogador)
```

Exemplo de dados:
```
Nome do jogador: Pedro
Posição: Atacante
ID do time: 1 (ou 0 para jogador livre)
```

Repita para cadastrar mais jogadores:
- Gabriel Barbosa (Atacante)
- Everton Ribeiro (Meio-campo)
- David Luiz (Defensor)
- Rossi (Goleiro)

### 4. Criar Time de Usuário

```
Menu Principal > 1 (Cadastros) > 4 (Criar Time de Usuário)
```

Exemplo de dados:
```
ID do usuário dono do time: 1 (João Silva)
Nome do time: Dream Team do João
```

### 5. Adicionar Jogadores ao Time de Usuário

```
Menu Principal > 1 (Cadastros) > 5 (Adicionar Jogador ao Time de Usuário)
```

Exemplo de dados:
```
ID do time de usuário: 1 (Dream Team do João)
ID do jogador: 1 (Pedro)
```

Repita para adicionar mais jogadores ao time.

### 6. Consultar Dados

```
Menu Principal > 2 (Consultas)
```

Opções disponíveis:
- **1** - Ver todos os usuários cadastrados
- **2** - Ver todos os times oficiais
- **3** - Ver todos os jogadores
- **4** - Ver times de usuário e seus jogadores
- **5** - Consultas avançadas (estatísticas)

## Dicas

1. Sempre cadastre usuários e times oficiais primeiro
2. Para cadastrar jogadores vinculados a times, os times devem existir
3. Use ID "0" ao cadastrar jogador para criar um "jogador livre" (sem time)
4. As consultas avançadas mostram estatísticas interessantes sobre os dados
5. Use Ctrl+C para sair do aplicativo a qualquer momento

## Consultas Avançadas

### Jogadores por Posição
Mostra quantos jogadores cada time oficial tem em cada posição (Atacante, Meio-campo, etc.)

### Jogadores Sem Time
Lista todos os jogadores que não estão vinculados a nenhum time oficial

### Jogadores do Time Preferido
Mostra quantos jogadores do time preferido de cada usuário estão nos times que ele criou
