# Documentação do Backend ComVoz

## Arquitetura Geral

O backend do ComVoz é construído usando Flask e segue uma arquitetura MVC (Model-View-Controller) com as seguintes características:

### Banco de Dados
- **Híbrido**: Utiliza dois bancos de dados:
  - **MySQL/SQLite**: Para dados estruturados (usuários, planos, etc.)
  - **MongoDB**: Para dados não estruturados (pesquisas, envios)

### Estrutura de Diretórios
```
flaskProject1/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── views/
│   ├── schemas/
│   ├── utils/
│   ├── middleware/
│   └── enums/
├── app.py
└── requirements.txt
```

## Módulos Principais

### 1. Autenticação e Usuários
- Gerenciamento de usuários
- Autenticação JWT
- Controle de acesso

### 2. Planos e Assinaturas
- Planos disponíveis:
  - Free (1 pesquisa, 20 envios)
  - Basic (5 pesquisas, 200 envios)
  - Pro (20 pesquisas, 1000 envios)
  - Enterprise (100 pesquisas, 10000 envios)

### 3. Pesquisas
- Criação e gerenciamento de pesquisas
- Tipos de questões suportadas
- Controle de limites por plano

### 4. Envios
- Gerenciamento de envios de pesquisas
- Estatísticas e relatórios
- Controle de respostas

### 5. Contatos
- Gerenciamento de contatos
- Importação via Excel/CSV
- Validação de dados

## Endpoints Disponíveis

Agora vou criar um arquivo JSON para importação no Postman com todos os endpoints. O arquivo será organizado nas seguintes coleções:

1. Autenticação
2. Usuários
3. Planos
4. Pesquisas
5. Questões
6. Envios
7. Contatos


Agora vou continuar com a documentação detalhada da arquitetura e lógicas de negócio:

# Documentação Técnica do Backend ComVoz

## Lógicas de Negócio

### 1. Sistema de Planos
- **Tipos de Planos:**
  - Free: 1 pesquisa, 20 envios
  - Basic: 5 pesquisas, 200 envios
  - Pro: 20 pesquisas, 1000 envios
  - Enterprise: 100 pesquisas, 10000 envios

- **Controle de Limites:**
  - Verificação de limite de pesquisas por plano
  - Verificação de limite de envios por pesquisa
  - Sistema de interesse em planos superiores

### 2. Sistema de Pesquisas
- **Tipos de Questões:**
  1. Múltipla Escolha
  2. Escala
  3. Texto Livre

- **Gestão de Pesquisas:**
  - Criação com questões personalizadas
  - Ativação/Desativação
  - Controle de respostas
  - Estatísticas e relatórios

### 3. Sistema de Envios
- **Funcionalidades:**
  - Envio para múltiplos contatos
  - Controle de status (concluído/não concluído)
  - Coleta de respostas
  - Geração de estatísticas

### 4. Gestão de Contatos
- **Recursos:**
  - Cadastro manual
  - Importação via Excel/CSV
  - Validação de dados
  - Associação com pesquisas

## Endpoints Disponíveis

### Autenticação
```
POST /login
POST /register
```

### Planos
```
GET /plans
GET /plan/{id}
POST /register_interest
```

### Pesquisas
```
POST /criar_pesquisa
GET /pesquisas
GET /pesquisas/{id}
```

### Questões
```
POST /criar_questoes
GET /get_questoes/{user_id}
```

### Envios
```
POST /envios
GET /envios
GET /envios/{id}
PUT /envios/{id}
GET /pesquisas/{id}/estatisticas
```

### Contatos
```
GET /contatos
POST /contatos
POST /contatos/by_excel
```

## Banco de Dados

### MySQL/SQLite (Dados Estruturados)
- Usuários
- Planos
- Questões
- Contatos
- Planos Contratados

### MongoDB (Dados Não Estruturados)
- Pesquisas
- Envios
- Respostas
- Estatísticas

## Segurança

### Autenticação
- JWT (JSON Web Tokens)
- Refresh Tokens
- Validação de senhas

### Autorização
- Middleware de verificação de token
- Controle de acesso baseado em planos
- Validação de limites

## Integrações

### Email
- Notificações de interesse em planos
- Envio de pesquisas
- Alertas de sistema

### Excel/CSV
- Importação de contatos
- Exportação de relatórios

O arquivo `postman_collection.json` foi gerado e contém todos os endpoints organizados em pastas, com exemplos de payloads e headers necessários para cada requisição. Para usar:

1. Importe o arquivo no Postman
2. Configure a variável de ambiente `base_url`
3. Obtenha um token via login
4. Use o token nas requisições que necessitam autenticação
