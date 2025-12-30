import hvac
from requests import post, get
from base64 import b64encode, b64decode
from os import environ
KUBERNETES_API_ADDRESS = 'https://kubernetes.default.svc'
STORED_SHARES = 5
SECRET_THRESHOLD = 3
VAULT_ADDRESS = environ.get('VAULT_ADDRESS')
KUBERNETES_SECRET_NAME = 'vault-secrets'


def get_current_namespace():
    with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
        return f.readline()


def get_token() -> str:
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
        return f.readline()


def get_ca_path() -> str:
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"


def is_sealed(client: hvac.Client) -> bool:
    return client.sys.is_sealed()


def is_initialized(client: hvac.Client) -> bool:
    return client.sys.is_initialized()


def initialize(client: hvac.Client) -> dict:
    return client.sys.initialize(secret_threshold=SECRET_THRESHOLD, secret_shares=STORED_SHARES)


def get_secret() -> str:
    secret_request = get(url=f"{KUBERNETES_API_ADDRESS}/api/v1/namespaces/{get_current_namespace()}/secrets/{KUBERNETES_SECRET_NAME}",
                         headers={"Accept": "application/json",
                                  "Content-Type": "application/json",
                                  'Authorization': f'Bearer {get_token()}'},
                         verify=get_ca_path())

    return secret_request.json()['data']['keys']


def unseal(client: hvac.Client) -> None:
    secret = get_secret()
    keys = b64decode(secret).decode('utf-8').split(',')
    for key in keys:
        client.sys.submit_unseal_key(key)

        if not is_sealed(client):
            print('Vault is unsealed.')
            break


def create_secret(keys: list,root_token: str) -> None:
    keys_data = b64encode(','.join(keys).encode()).decode()
    root_token_data = b64encode(root_token.encode()).decode()
    current_namespace = get_current_namespace()
    request_body = {"kind": "Secret",
                    "apiVersion": "v1",
                    "metadata": {"name": KUBERNETES_SECRET_NAME},
                    "data": {
                            "keys": keys_data,
                            "root_token": root_token_data,
                        }
                    }

    request = post(url=f"{KUBERNETES_API_ADDRESS}/api/v1/namespaces/{current_namespace}/secrets",
                   headers={"Content-Type": "application/json",
                            "Accept": "application/json",
                            'Authorization': f'Bearer {get_token()}'},
                   json=request_body,
                   verify=get_ca_path())

    if request.status_code > 299 or request.status_code < 200:
        raise Exception(f"Unable to init: {request.text}")
    return


def main():
    client = hvac.Client(url=VAULT_ADDRESS)

    if is_sealed(client):
        if not is_initialized(client):
            print("Vault is not initialized. Initializing Vault...")
            init = initialize(client)
            create_secret(init['keys'], init['root_token'])
            print("Vault initialized.")
        print("Vault is sealed. Unsealing Vault...")
        unseal(client)
    else:
        print("Vault is not sealed. Nothing to do...")


if __name__ == '__main__':
    main()
