"""Nível 2, caminho B: gera imagem ou vídeo na API da Magnific com a sua API key.

Uso:
    python tools/magnific_api.py <endpoint> <argumentos.json ou JSON direto> <pasta de saída> [endpoint de consulta]

Exemplo:
    python tools/magnific_api.py text-to-image/seedream-v5-pro '{"prompt": "paper-cut desk", "aspect_ratio": "9:16"}' "projetos/001. meu-video/magnific"

O <endpoint> é o caminho do modelo depois de /v1/ai/, como está na página do modelo em https://docs.magnific.com.
A tarefa é consultada em <endpoint>/<task_id>. Se a página do modelo indicar outro caminho de consulta, passe-o como quarto argumento.
Credencial (criada em https://www.magnific.com/user/organization/api-keys), numa variável de ambiente, nunca em arquivo do repositório:
    MAGNIFIC_API_KEY="sua-api-key"
Os links de resultado expiram em 30 minutos: o script baixa tudo assim que a tarefa termina.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ.get("MAGNIFIC_API_BASE", "https://api.magnific.com")
ESPERA_S, LIMITE_S = 5, 20 * 60
CABECALHO = {"Accept": "application/json", "User-Agent": "studio-magnific/1.0"}


def caminho(endpoint):
    endpoint = endpoint.strip("/")
    return f"/{endpoint}" if endpoint.startswith("v1/") else f"/v1/ai/{endpoint}"


def chamar(metodo, rota, chave, corpo=None):
    dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
    cabecalho = {**CABECALHO, "x-magnific-api-key": chave, "Content-Type": "application/json"}
    pedido = urllib.request.Request(BASE + rota, data=dados, method=metodo, headers=cabecalho)
    try:
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            return json.load(resposta)
    except urllib.error.HTTPError as erro:
        sys.exit(f"HTTP {erro.code} em {metodo} {rota}: {erro.read().decode('utf-8', 'replace')[:2000]}")


# ponytail: o formato de `generated` muda de modelo para modelo (lista de URLs ou de objetos), então pega toda URL http.
def urls(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from urls(v)
    elif isinstance(x, list):
        for v in x:
            yield from urls(v)
    elif isinstance(x, str) and x.startswith("http"):
        yield x


def baixar(url, destino):
    with urllib.request.urlopen(urllib.request.Request(url, headers=CABECALHO), timeout=300) as resposta:
        destino.write_bytes(resposta.read())


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    endpoint, bruto, saida = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    consulta = caminho(sys.argv[4] if len(sys.argv) > 4 else endpoint)
    chave = os.environ.get("MAGNIFIC_API_KEY")
    if not chave:
        sys.exit("Defina a variável de ambiente MAGNIFIC_API_KEY (veja guias/4-nivel-2-magnific.md).")
    argumentos = json.loads(bruto if bruto.lstrip().startswith("{") else Path(bruto).read_text(encoding="utf-8"))
    saida.mkdir(parents=True, exist_ok=True)

    resultado = chamar("POST", caminho(endpoint), chave, argumentos)
    dados = resultado.get("data") or {}
    tarefa, inicio = dados.get("task_id"), time.time()
    while tarefa and dados.get("status") not in ("COMPLETED", "FAILED"):
        if time.time() - inicio > LIMITE_S:
            sys.exit(f"Tempo esgotado: a tarefa {tarefa} ainda está em {dados.get('status')}.")
        time.sleep(ESPERA_S)
        resultado = chamar("GET", f"{consulta}/{tarefa}", chave)
        dados = resultado.get("data") or {}
        print(f"{dados.get('status')} - {int(time.time() - inicio)} s", file=sys.stderr)

    registro = saida / "ultimo-resultado.json"
    registro.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    if dados.get("status") == "FAILED":
        sys.exit(f"A tarefa {tarefa} falhou. Detalhes em {registro}.")

    nome = endpoint.strip("/").replace("/", "_")
    for i, url in enumerate(urls(dados.get("generated", resultado))):
        destino = saida / f"{nome}_{i}{Path(url.split('?')[0]).suffix or '.bin'}"
        baixar(url, destino)
        print(destino)


if __name__ == "__main__":
    main()
