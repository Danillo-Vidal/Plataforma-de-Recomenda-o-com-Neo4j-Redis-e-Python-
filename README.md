# CP2 - Plataforma de Recomendação com Neo4j, Redis e Python

Projeto da FIAP: uma API de recomendação de filmes usando **Neo4j** (grafo), **Redis** (cache) e **Python com FastAPI**.

## O que o projeto faz

- Cadastra usuários, filmes e gêneros
- Registra filmes assistidos e avaliações
- Gera recomendações personalizadas com base nos gêneros que o usuário mais avaliou bem
- Armazena as recomendações em cache no Redis (com TTL)
- Identifica CACHE HIT e CACHE MISS
- Permite invalidar o cache

## Tecnologias

- **Neo4j Aura** (banco de grafos, free tier)
- **Redis** (rodando via Docker)
- **FastAPI** (Python)
- **Docker Compose** (para subir o Redis local)

## Modelagem do grafo

```
(Usuario) -[:ASSISTIU]-> (Filme)
(Usuario) -[:AVALIOU {nota}]-> (Filme)
(Filme) -[:PERTENCE_A]-> (Genero)
```

## Como rodar localmente

### 1. Pré-requisitos
- Python 3.12+
- Docker Desktop
- Uma instância Neo4j Aura (free tier) já criada

### 2. Clonar e configurar

```bash
git clone <seu-repo>
cd cp2-recomendacao
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Configurar o `.env`

Crie um arquivo `.env` na raiz do projeto com as credenciais da sua instância Neo4j Aura:

```dotenv
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sua-senha-aqui
NEO4J_DATABASE=neo4j

REDIS_HOST=localhost
REDIS_PORT=6379
```

> Atenção: salve o arquivo como UTF-8 (sem BOM), senão o Python pode não conseguir ler a primeira variável.

### 4. Popular o banco (Neo4j)

Cole o script abaixo no Query do Neo4j Aura pra criar os dados de teste:

```cypher
CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT genero_nome IF NOT EXISTS FOR (g:Genero) REQUIRE g.nome IS UNIQUE;
CREATE CONSTRAINT filme_id IF NOT EXISTS FOR (f:Filme) REQUIRE f.id IS UNIQUE;

CREATE (:Usuario {id: 1, nome: 'Dan', email: 'dan@teste.com', idade: 22});
CREATE (:Usuario {id: 2, nome: 'Mari', email: 'mari@teste.com', idade: 22});
CREATE (:Usuario {id: 3, nome: 'Matheus', email: 'teteuze@teste.com', idade: 18});

CREATE (:Filme {id: 1, nome: 'Matrix'});
CREATE (:Filme {id: 2, nome: 'Interestelar'});
CREATE (:Filme {id: 3, nome: 'Duna'});

CREATE (:Genero {nome: 'Ficção Científica'});
CREATE (:Genero {nome: 'Drama'});
CREATE (:Genero {nome: 'Ação'});

MATCH (g:Genero {nome:'Ficção Científica'}) SET g.id = 1;
MATCH (g:Genero {nome:'Drama'}) SET g.id = 2;
MATCH (g:Genero {nome:'Ação'}) SET g.id = 3;

MATCH (f:Filme {id: 2}) MATCH (g:Genero {nome: 'Drama'}) CREATE (f)-[:PERTENCE_A]->(g);
MATCH (f:Filme {id: 3}) MATCH (g:Genero {id: 1}) CREATE (f)-[:PERTENCE_A]->(g);
MATCH (f:Filme {id: 1}) MATCH (g:Genero {id: 3}) CREATE (f)-[:PERTENCE_A]->(g);

MATCH (u:Usuario{id: 1}) MATCH (f:Filme {id: 3}) CREATE (u)-[:AVALIOU {nota: 10}]->(f);
MATCH (u:Usuario{id: 2}) MATCH (f:Filme {id: 1}) CREATE (u)-[:AVALIOU {nota: 10}]->(f);
MATCH (u:Usuario{id: 2}) MATCH (f:Filme {id: 2}) CREATE (u)-[:AVALIOU {nota: 5}]->(f);

MATCH (u:Usuario{id: 2}) MATCH (f:Filme {id: 2}) CREATE (u)-[:ASSISTIU]->(f);
```

### 5. Subir o Redis

```bash
docker compose up -d
```

### 6. Rodar a API

```bash
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/docs` pra ver e testar os endpoints (Swagger).

## Endpoints disponíveis

| Método | Rota | O que faz |
|---|---|---|
| GET | `/` | Health check |
| GET | `/test/neo4j` | Testa conexão com Neo4j |
| GET | `/test/redis` | Testa conexão com Redis |
| POST | `/usuarios` | Cadastra usuário |
| POST | `/filmes` | Cadastra filme |
| POST | `/generos` | Cadastra gênero |

## Status do projeto

- [x] Modelagem do grafo no Neo4j
- [x] Conexão Python + FastAPI + Neo4j + Redis
- [x] Endpoints de cadastro (usuário, filme, gênero)
- [ ] Endpoints de registro (assistiu, avaliou)
- [ ] Endpoint de recomendação
- [ ] Cache no Redis (TTL, HIT/MISS, invalidação)
- [ ] Testes de desempenho
