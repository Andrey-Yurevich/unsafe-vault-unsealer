# unsafe-vault-unsealer

⚠️ **WARNING: NEVER USE IN PRODUCTION**

## Description
Small Python script that ensures **Vault running in Kubernetes** is:
- initialized
- unsealed after pod/container restart

Stores **unseal keys and root token in a Kubernetes Secret**, which makes it **inherently insecure**.

---

## How it works
- Connects to Vault
- If Vault is not initialized → initializes it
- Saves unseal keys and root token to a Kubernetes Secret
- If Vault is sealed → unseals it using stored keys
- If unsealed → exits

---

## Requirements
- Runs inside Kubernetes
- ServiceAccount with permissions:
  - `get` secrets
  - `create` secrets
- Access to Kubernetes API

---

## Environment variables

| Variable | Description |
|--------|------------|
| `VAULT_ADDRESS` | Vault address (e.g. `http://vault:8200`) |

---

## Hardcoded settings
- Unseal keys: `5`
- Threshold: `3`
- Secret name: `vault-secrets`

---

## Dependencies
- Python 3
- `hvac`
- `requests`

---

## Why unsafe
- Unseal keys stored in plain Kubernetes Secret
- Root token stored in Secret

**For learning and testing only.**