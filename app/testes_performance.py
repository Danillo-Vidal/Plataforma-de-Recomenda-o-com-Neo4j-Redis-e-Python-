import requests
import time

BASE_URL = "http://127.0.0.1:8000"
USUARIO_ID = 1
NUM_REQUISICOES = 20

def medir(rotulo, n):
    tempos = []
    for _ in range(n):
        inicio = time.perf_counter()
        resposta = requests.get(f"{BASE_URL}/recomendacoes/{USUARIO_ID}")
        fim = time.perf_counter()
        tempos.append((fim - inicio) * 1000)

        print(f"  status: {resposta.status_code} | tempo: {tempos[-1]:.2f} ms | corpo: {resposta.text[:100]}")

    media = sum(tempos) / len(tempos)
    print(f"{rotulo}: média {media:.2f} ms | min {min(tempos):.2f} ms | max {max(tempos):.2f} ms")
    return tempos

if __name__ == "__main__":
    requests.delete(f"{BASE_URL}/recomendacoes/{USUARIO_ID}/cache")
    print("1ª chamada (deve ser CACHE MISS):")
    medir("MISS", 1)
    print(f"\nPróximas {NUM_REQUISICOES} chamadas (devem ser CACHE HIT):")
    medir("HIT", NUM_REQUISICOES)