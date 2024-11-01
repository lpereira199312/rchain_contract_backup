import requests
import os
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Desabilita o aviso de InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_contrato_info(wallet_address):
    url = "https://test.reactioon.network:8080/rchain/contract/list/signed"
    headers = {
        "Host": "test.reactioon.network:8080",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Content-Length": "53"
    }
    data = f"wallet={wallet_address}&limit=10000"
    
    response = requests.post(url, headers=headers, data=data, verify=False)
    return response

def sanitize_filename(filename):
    # Substitui espaços por underscores e remove caracteres inválidos
    filename = filename.replace(" ", "_")
    # Remove caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    # Garante que o arquivo não comece com um ponto
    if filename.startswith('.'):
        filename = '_' + filename[1:]  # Substitui o ponto inicial por um underscore
    return filename

def download_file(url, filename):
    response = requests.get(url, verify=False)
    response.raise_for_status()  # Lança uma exceção se o download falhar
    
    # Sanitiza o nome do arquivo
    filename = sanitize_filename(filename) + ".txt"
    
    # Verifica se o arquivo já existe e faz uma variação no nome, se necessário
    base_filename = filename
    counter = 1
    while os.path.exists(base_filename):
        base_filename = f"{filename.rsplit('.', 1)[0]}_{counter}.txt"
        counter += 1
    
    # Salva o conteúdo do arquivo
    with open(base_filename, 'wb') as file:
        file.write(response.content)
    
    print(f"Arquivo salvo como: {base_filename}")

# Exemplo de uso
wallet_address = input("Digite o endereço da wallet: ")
print("\nPegando informações...")

response = get_contrato_info(wallet_address)

try:
    response_data = response.json()
    contract_data = response_data.get("response", [])
    
    for contract in contract_data:
        wallet = contract.get("wallet")
        if wallet == wallet_address:
            name = contract.get("name")
            hash_contract = contract.get("contract_hash")
            
            # Verifica se 'name' e 'hash_contract' existem e não estão vazios
            if not name or not hash_contract:
                continue  # Ignora esse contrato e passa para o próximo
            
            print(f"Contract Name: {name}")
            print(f"Hash Contract: {hash_contract}\n")
            
            # URL para download do arquivo
            url_download = f"https://test.reactioon.network:8080/rchain/storage/show?dsh={hash_contract}"
            print(f"URL Download: {url_download}\n")
            
            # Pergunta ao usuário se deseja fazer o download
            download_confirmation = input(f"Deseja fazer o download do arquivo '{sanitize_filename(name)}.txt'? (s/n): ").strip().lower()
            if download_confirmation == 's':
                # Baixa e salva o arquivo
                download_file(url_download, name)
            else:
                print("Download cancelado pelo usuário.\n")
except ValueError:
    print("Erro ao decodificar a resposta JSON.")
except KeyError as e:
    print(f"Chave não encontrada: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")

