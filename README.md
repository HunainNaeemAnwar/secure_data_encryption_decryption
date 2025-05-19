# 🔐 Secure Data Vault

A secure, local Streamlit application for storing and retrieving encrypted data using user-defined passkeys.  
It includes built-in lockout protection and reauthorization features to prevent brute-force attacks and unauthorized access.

---

## 📌 Features

- **Fernet Encryption** (AES-128 based) for secure data handling
- **SHA-256 Hashing** for passkeys
- **3-Attempt Lockout System** to prevent brute-force access
- **Reauthorization Option** after lockout timeout
- **Local JSON Storage** – no external databases required
- **Clean Streamlit UI** for easy use

---

## 🛠️ Requirements

- Python 3.8 or above  
- Libraries:
  - `streamlit`
  - `cryptography`

Install dependencies:

```bash
pip install streamlit cryptography
