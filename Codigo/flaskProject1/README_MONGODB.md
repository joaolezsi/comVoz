# Configuração do MongoDB para o Sistema de Pesquisas NPS

Este documento descreve a configuração e uso do MongoDB no sistema de pesquisas NPS da ComVoz.

## Visão Geral da Arquitetura

O sistema utiliza uma arquitetura de banco de dados híbrida:
- **SQLite/MySQL**: para autenticação de usuários e operações básicas
- **MongoDB**: para armazenamento das pesquisas, envios e empresas (dados não estruturados)

## Instalação do MongoDB

### Windows

1. Baixe o MongoDB Community Server em: https://www.mongodb.com/try/download/community
2. Instale seguindo as instruções do instalador
3. O MongoDB roda por padrão na porta 27017

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y mongodb

# Iniciar serviço
sudo systemctl start mongodb
```

### Docker (alternativa para qualquer plataforma)

```bash
# Puxar imagem e iniciar container
docker pull mongo
docker run -d -p 27017:27017 --name mongodb-comvoz mongo

# Verificar se está rodando
docker ps
```

## Configuração do Projeto

1. Copie o arquivo `env.example` para `.env`:
   ```bash
   cp env.example .env
   ```

2. Edite o arquivo `.env` com suas configurações:
   ```
   # MongoDB configuration
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=comvoz_nps
   ```

## Estrutura do Banco de Dados

O MongoDB é usado para armazenar três tipos principais de documentos:

### 1. Pesquisas (Collection: `pesquisas`)

```json
{
    "_id": "ObjectId",
    "titulo": "Pesquisa de Satisfação 2024",
    "descricao": "Pesquisa anual de satisfação dos colaboradores",
    "perguntas": [
        {
            "pergunta": "Como você avalia o ambiente de trabalho?",
            "tipo": "escala",
            "opcoes": ["1", "2", "3", "4", "5"]
        },
        {
            "pergunta": "Você recomendaria a empresa para um amigo?",
            "tipo": "booleano",
            "opcoes": ["Sim", "Não"]
        }
    ],
    "data_criacao": "ISODate",
    "empresa_id": "ObjectId",
    "ativa": true
}
```

### 2. Envios (Collection: `envios`)

```json
{
    "_id": "ObjectId",
    "pesquisa_id": "ObjectId",
    "usuario": {
        "nome": "João Silva",
        "email": "joao.silva@empresa.com"
    },
    "respostas": [
        {
            "pergunta_id": 0,
            "pergunta": "Como você avalia o ambiente de trabalho?",
            "resposta": "4"
        },
        {
            "pergunta_id": 1,
            "pergunta": "Você recomendaria a empresa para um amigo?",
            "resposta": "Sim"
        }
    ],
    "data_envio": "ISODate",
    "concluido": true,
    "empresa_id": "ObjectId"
}
```

### 3. Empresas (Collection: `empresas`)

```json
{
    "_id": "ObjectId",
    "nome": "Empresa ABC",
    "cnpj": "12345678901234",
    "segmento": "Tecnologia",
    "contato": {
        "email": "contato@empresa.com",
        "telefone": "(11) 1234-5678"
    },
    "pesquisas": [
        {
            "pesquisa_id": "ObjectId",
            "titulo": "Pesquisa de Satisfação 2024",
            "data_criacao": "ISODate",
            "nota": 8.5,
            "meta": 9.0
        }
    ],
    "data_cadastro": "ISODate",
    "plano": {
        "tipo": "Premium",
        "pesquisas_anuais": 4,
        "data_inicio": "ISODate",
        "data_fim": "ISODate"
    },
    "ativa": true
}
```

## Ferramentas Recomendadas para Administração

Para gerenciar e visualizar seus dados MongoDB, recomendamos:

1. **MongoDB Compass**: Interface gráfica oficial do MongoDB
   - Download: https://www.mongodb.com/try/download/compass

2. **Studio 3T**: Ferramenta completa com interface visual
   - Download: https://studio3t.com/download/

3. **NoSQLBooster**: Alternativa com interface amigável
   - Download: https://nosqlbooster.com/downloads

## Operações Comuns via MongoDB Shell

Você pode usar o MongoDB Shell para operações básicas:

```javascript
// Conectar ao banco
mongo

// Selecionar o banco
use comvoz_nps

// Listar pesquisas
db.pesquisas.find().pretty()

// Buscar pesquisa por título
db.pesquisas.find({titulo: /Satisfação/}).pretty()

// Contar envios concluídos por pesquisa
db.envios.countDocuments({pesquisa_id: ObjectId("id_da_pesquisa"), concluido: true})

// Buscar empresas ativas
db.empresas.find({ativa: true}).pretty()
```

## Backup e Restauração

Para fazer backup do MongoDB:

```bash
# Backup
mongodump --db=comvoz_nps --out=/caminho/para/backup

# Restauração
mongorestore --db=comvoz_nps /caminho/para/backup/comvoz_nps
```

## Solução de Problemas

### Conexão Recusada
- Verifique se o MongoDB está rodando: `systemctl status mongodb` (Linux) ou verifique nos Serviços (Windows)
- Verifique se a porta 27017 está acessível: `telnet localhost 27017`

### Erros de Autenticação
- Verifique se o usuário e senha estão corretos no arquivo `.env`
- Confirme se o usuário tem acesso ao banco de dados específico

### Consultas não retornam resultados
- Verifique se está usando o ID correto (o ObjectId é sensível)
- Use `.explain()` para analisar como a consulta está sendo executada

## Recursos Adicionais

- [Documentação oficial do MongoDB](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB University](https://university.mongodb.com/) - Cursos gratuitos 