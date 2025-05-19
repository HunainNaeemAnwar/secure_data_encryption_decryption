# --- Required Imports ---
import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import json
import os
import time

# --- Configuration ---
DATA_FILE = "data.json"
KEY_FILE = "fernet.key"
ATTEMPTS_LIMIT = 3
LOCKOUT_TIME = 30  # seconds

# --- Key Handling ---
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        KEY = f.read()
else:
    KEY = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(KEY)

cipher = Fernet(KEY)

# --- Data Handling ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        stored_data = json.load(f)
else:
    stored_data = {}

# --- Session State Init ---
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = {}

if "lockout_timers" not in st.session_state:
    st.session_state.lockout_timers = {}

# --- Utility Functions ---
def hash_passkey(passkey: str) -> str:
    return hashlib.sha256(passkey.encode()).hexdigest()

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(stored_data, f)

def encrypt_data(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text: str) -> str:
    return cipher.decrypt(encrypted_text.encode()).decode()

# --- UI Starts Here ---
st.title("Secure Data Vault")

menu = ["Home", "Store Data", "Retrieve Data", "Reauthorize"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- Home Page ---
if choice == "Home":
    st.subheader("Welcome")
    st.write("This application securely stores and retrieves encrypted data using passkeys.")

# --- Store New Data ---
elif choice == "Store Data":
    st.subheader("Store New Data")
    username = st.text_input("Username:")
    user_data = st.text_area("Data:")
    passkey = st.text_input("Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if username and user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data)
            stored_data[username] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            save_data()
            st.success("Data stored securely.")
        else:
            st.error("All fields are required.")

# --- Retrieve Data ---
elif choice == "Retrieve Data":
    st.subheader("Retrieve Stored Data")
    username = st.text_input("Username:")
    passkey = st.text_input("Passkey:", type="password")

    # Lockout Check
    if username in st.session_state.lockout_timers:
        remaining = int(st.session_state.lockout_timers[username] - time.time())
        if remaining > 0:
            st.warning(f"Too many failed attempts. Please wait {remaining} seconds.")
            with st.empty():
                for i in range(remaining, 0, -1):
                    st.info(f"Unlocking in {i} seconds...")
                    time.sleep(1)
                st.rerun()
        else:
            del st.session_state.lockout_timers[username]
            st.session_state.failed_attempts[username] = 0
            st.rerun()

    elif st.button("Decrypt"):
        if username and passkey:
            if username in stored_data:
                hashed_input = hash_passkey(passkey)
                real_hash = stored_data[username]["passkey"]

                if hashed_input == real_hash:
                    decrypted = decrypt_data(stored_data[username]["encrypted_text"])
                    st.success(f"Decrypted Data: {decrypted}")
                    st.session_state.failed_attempts[username] = 0
                else:
                    st.session_state.failed_attempts[username] = st.session_state.failed_attempts.get(username, 0) + 1
                    remaining_attempts = ATTEMPTS_LIMIT - st.session_state.failed_attempts[username]
                    st.error(f"Incorrect passkey. Attempts left: {remaining_attempts}")

                    if st.session_state.failed_attempts[username] >= ATTEMPTS_LIMIT:
                        st.session_state.lockout_timers[username] = time.time() + LOCKOUT_TIME
                        st.warning("Too many failed attempts. Locking temporarily.")
                        st.rerun()
            else:
                st.error("Username not found.")
        else:
            st.error("All fields are required.")

# --- Reauthorization ---
elif choice == "Reauthorize":
    st.subheader("Reauthorize Access")
    username = st.text_input("Username:")
    passkey = st.text_input("Master Passkey:", type="password")

    if st.button("Login"):
        if username in stored_data and passkey:
            hashed = hash_passkey(passkey)
            if stored_data[username]["passkey"] == hashed:
                st.session_state.failed_attempts[username] = 0
                st.session_state.lockout_timers.pop(username, None)
                st.success("Access restored. You may try again.")
            else:
                st.error("Incorrect passkey.")
        else:
            st.error("Invalid username or passkey.")
