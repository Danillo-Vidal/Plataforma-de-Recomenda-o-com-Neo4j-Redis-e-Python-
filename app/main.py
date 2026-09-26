import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from datetime import date

load_dotenv()  # carrega o .env pro ambiente

# --- Configuração da conexão com o Neo4j Aura ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

app = FastAPI(title="API de Recomendação")


# --- Modelos de entrada ---
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    idade: int


class Filme(BaseModel):
    id: int
    nome: str
    ano: int

class FilmeUpdate(BaseModel):
    nome: str
    ano: int

class Genero(BaseModel):
    id: int
    nome: str


class Assistiu(BaseModel):
    usuario_id: int
    filme_id: int
    data: str | None = None  # formato "YYYY-MM-DD", opcional


class Avaliou(BaseModel):
    usuario_id: int
    filme_id: int
    nota: float
    data: str | None = None


# --- Cadastro de usuário ---
@app.post("/usuarios")
def criar_usuario(usuario: Usuario):
    with driver.session() as session:
        session.run(
            """
            MERGE (u:Usuario {id: $id})
            ON CREATE SET u.nome = $nome, u.email = $email, u.idade = $idade
            ON MATCH SET u.nome = $nome, u.email = $email, u.idade = $idade
            """,
            id=usuario.id, nome=usuario.nome, email=usuario.email, idade=usuario.idade
        )
    return {"status": "criado ou atualizado", "usuario": usuario}


# --- Cadastro de filme ---
@app.post("/filmes")
def criar_filme(filme: Filme):
    with driver.session() as session:
        session.run(
            """
            MERGE (f:Filme {id: $id})
            ON CREATE SET f.nome = $nome, f.ano = $ano
            ON MATCH SET f.nome = $nome, f.ano = $ano
            """,
            id=filme.id, nome=filme.nome, ano=filme.ano
        )
    return {"status": "criado", "filme": filme}

# --- Atualizar filme ---
@app.put("/filmes/{filme_id}")
def atualizar_filme(filme_id: int, filme: FilmeUpdate):
    with driver.session() as session:
        resultado = session.run(
            """
            MATCH (f:Filme {id: $filme_id})
            SET f.nome = $nome, f.ano = $ano
            RETURN f.id AS id, f.nome AS nome, f.ano AS ano
            """,
            filme_id=filme_id, nome=filme.nome, ano=filme.ano
        )
        registro = resultado.single()

    if not registro:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    return {"status": "atualizado", "filme": dict(registro)}

# --- Deletar filme ---
@app.delete("/filmes/{filme_id}")
def deletar_filme(filme_id: int):
    with driver.session() as session:
        resultado = session.run(
            """
            MATCH (f:Filme {id: $filme_id})
            DETACH DELETE f
            RETURN count(f) AS deletados
            """,
            filme_id=filme_id
        )
        registro = resultado.single()

    if registro["deletados"] == 0:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    return {"status": "deletado", "filme_id": filme_id}

# --- Cadastro de gênero ---
@app.post("/generos")
def criar_genero(genero: Genero):
    with driver.session() as session:
        session.run(
            """
            MERGE (g:Genero {id: $id})
            ON CREATE SET g.nome = $nome
            """,
            id=genero.id, nome=genero.nome
        )
    return {"status": "criado", "genero": genero}


# --- Registrar filme assistido ---
@app.post("/assistidos")
def registrar_assistido(registro: Assistiu):
    data_registro = registro.data or date.today().isoformat()

    with driver.session() as session:
        resultado = session.run(
            """
            MATCH (u:Usuario {id: $usuario_id})
            MATCH (f:Filme {id: $filme_id})
            MERGE (u)-[r:ASSISTIU]->(f)
            ON CREATE SET r.data = date($data)
            RETURN u.nome AS usuario, f.nome AS filme
            """,
            usuario_id=registro.usuario_id, filme_id=registro.filme_id, data=data_registro
        )
        registro_criado = resultado.single()

    if not registro_criado:
        raise HTTPException(status_code=404, detail="Usuário ou filme não encontrado")

    return {"status": "registrado", "usuario": registro_criado["usuario"], "filme": registro_criado["filme"]}

# --- Registrar avaliação ---
@app.post("/avaliacoes")
def registrar_avaliacao(registro: Avaliou):
    data_registro = registro.data or date.today().isoformat()

    if not (0 <= registro.nota <= 5):
        raise HTTPException(status_code=400, detail="Nota deve estar entre 0 e 5")

    with driver.session() as session:
        resultado = session.run(
            """
            MATCH (u:Usuario {id: $usuario_id})
            MATCH (f:Filme {id: $filme_id})
            MERGE (u)-[r:AVALIOU]->(f)
            ON CREATE SET r.nota = $nota, r.data = date($data)
            ON MATCH SET r.nota = $nota, r.data = date($data)
            RETURN u.nome AS usuario, f.nome AS filme, r.nota AS nota
            """,
            usuario_id=registro.usuario_id, filme_id=registro.filme_id,
            nota=registro.nota, data=data_registro
        )
        registro_criado = resultado.single()

    if not registro_criado:
        raise HTTPException(status_code=404, detail="Usuário ou filme não encontrado")

    return {
        "status": "registrado",
        "usuario": registro_criado["usuario"],
        "filme": registro_criado["filme"],
        "nota": registro_criado["nota"]
    }


@app.on_event("shutdown")
def fechar_conexao():
    driver.close()