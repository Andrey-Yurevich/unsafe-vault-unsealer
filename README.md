# unsafe-vault-unsealer

⚠️ **WARNING: FOR TEST ENVS ONLY. NEVER USE IN PRODUCTION**

## Description
Small Python script that ensures HashiCorp Vault(hosted in Kubernetes) is:
- initialized
- unsealed after pod/container restart

---

## How it works
- Connects to Vault
- If Vault is not initialized - initializes it
- Saves unseal keys and root token to a Kubernetes Secret
- If Vault is sealed - unseals it using stored keys
- If unsealed - exits

---

## Input Environment variables

| Variable        | Description                              |
|-----------------|------------------------------------------|
| `VAULT_ADDRESS` | Vault address (e.g. `http://vault:8200`) |
---

**For learning and testing only.**