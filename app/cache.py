import json
from app.redis_client import redis_client

CACHE_TTL_SEGUNDOS = 300


def obter_cache(chave: str):
    """Busca um valor no cache. Retorna None se não existir (CACHE MISS)."""
    valor = redis_client.get(chave)
    if valor is None:
        return None
    return json.loads(valor)


def salvar_cache(chave: str, valor, ttl: int = CACHE_TTL_SEGUNDOS):
    """Salva um valor no cache com TTL (em segundos)."""
    redis_client.setex(chave, ttl, json.dumps(valor))


def invalidar_cache(chave: str) -> bool:
    """Remove uma chave do cache. Retorna True se havia algo pra remover."""
    return redis_client.delete(chave) > 0