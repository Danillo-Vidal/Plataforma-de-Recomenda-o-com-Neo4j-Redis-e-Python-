from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.database import get_session
from app.redis_client import redis_client

app = FastAPI(title="API de Recomendação")

# ===== MODELOS (formato esperado no corpo da requisição) =====

class UsuarioCreate(BaseModel):
    id: int
    nome: str
    email: str
    idade: int

class FilmeCreate(BaseModel):
    id: int
    nome: str

class GeneroCreate(BaseModel):
    id: int
    nome: str

# ===== HEALTH CHECK =====

@app.get("/")
def health_check():
    return {"status": "API rodando"}

# ===== USUÁRIOS =====

@app.post("/usuarios")
def criar_usuario(usuario: UsuarioCreate):
    with get_session() as session:
        session.run(
            """
            CREATE (:Usuario {id: $id, nome: $nome, email: $email, idade: $idade})
            """,
            id=usuario.id, nome=usuario.nome, email=usuario.email, idade=usuario.idade
        )
    return {"mensagem": "Usuário criado", "usuario": usuario}

# ===== FILMES =====

@app.post("/filmes")
def criar_filme(filme: FilmeCreate):
    with get_session() as session:
        session.run(
            "CREATE (:Filme {id: $id, nome: $nome})",
            id=filme.id, nome=filme.nome
        )
    return {"mensagem": "Filme criado", "filme": filme}

# ===== GÊNEROS =====

@app.post("/generos")
def criar_genero(genero: GeneroCreate):
    with get_session() as session:
        session.run(
            "CREATE (:Genero {id: $id, nome: $nome})",
            id=genero.id, nome=genero.nome
        )
    return {"mensagem": "Gênero criado", "genero": genero}