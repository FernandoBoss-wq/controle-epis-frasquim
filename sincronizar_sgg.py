import base64
from datetime import datetime
import json
import requests

# 1. Configurações da API SGG
API_KEY = "SUA_CHAVE_API_AQUI"  # Chave de 32 caracteres obtida no painel SGG
BASE_URL = "https://app.sgg.net.br/api"

# Autenticação HTTP Basic (Chave: sem senha)
auth_token = base64.b64encode(f"{API_KEY}:".encode("utf-8")).decode("utf-8")
headers = {
    "Authorization": f"Basic {auth_token}",
    "Content-Type": "application/json",
}


def sincronizar():
  print(f"[{datetime.now().strftime('%H:%M:%S')}] Conectando à API SGG...")

  try:
    # Busca movimentações de EPIs
    res = requests.get(
        f"{BASE_URL}/movimentacaoEstoqueEPIs/", headers=headers, timeout=30
    )

    if res.status_code == 200:
      dados_api = res.json()
      lista_processada = []

      for idx, item in enumerate(dados_api):
        epi_nome = item.get("epi_descricao", "").upper()

        # Regra de negócio: Ignorar Protetor Concha se desejado
        if "CONCHA" in epi_nome:
          continue

        lista_processada.append({
            "id": idx + 1,
            "empresa": "FRASQUIM INDUSTRIA E COMERCIO LTDA",
            "funcionario": item.get("funcionario_nome", "Colaborador"),
            "funcao": item.get("cargo_nome", "Operacional"),
            "epi": epi_nome,
            "entregar_ate": item.get("data_vencimento", ""),
            "situacao": item.get("situacao", "Vencido"),
            "status_entrega": "Pendente",
            "data_entrega_real": "",
            "obs": "",
        })

      # Salva os dados atualizados para o painel web consumir
      payload = {
          "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
          "dados": lista_processada,
      }

      with open("dados_epis.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

      print(
          f"Sincronização concluída! {len(lista_processada)} registros"
          " atualizados."
      )

    else:
      print(f"Erro na API ({res.status_code}): {res.text}")

  except Exception as e:
    print(f"Falha de conexão: {e}")


if __name__ == "__main__":
  sincronizar()