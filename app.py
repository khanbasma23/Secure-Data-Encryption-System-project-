import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Generate a key (in real apps, store this securely)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# In-memory storage
stored_data = {}  # Format: {encrypted_text: {"encrypted_text": ..., "passkey": ...}}
failed_attempts = 0

# --- Utility Functions ---

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    global failed_attempts
    hashed_passkey = hash_passkey(passkey)

    for key, value in stored_data.items():
        if value["encrypted_text"] == encrypted_text and value["passkey"] == hashed_passkey:
            failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    
    failed_attempts += 1
    return None

# --- Streamlit UI ---

st.set_page_config(page_title="Secure Encryption", layout="centered")
st.title("🔒 Secure Data Encryption System")

menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- Home Page ---
if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

# --- Store Data Page ---
elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")

    user_data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data, passkey)
            stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            st.success("✅ Data stored securely!")
            st.code(encrypted_text)
        else:
            st.error("⚠️ Both fields are required!")

# --- Retrieve Data Page ---
elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")

    encrypted_text = st.text_area("Enter Encrypted Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_text and passkey:
            decrypted_text = decrypt_data(encrypted_text, passkey)
            if decrypted_text:
                st.success("✅ Decrypted Data:")
                st.code(decrypted_text)
            else:
                st.error(f"❌ Incorrect passkey! Attempts remaining: {3 - failed_attempts}")
                if failed_attempts >= 3:
                    st.warning("🔒 Too many failed attempts! Redirecting to Login Page.")
                    st.experimental_rerun()
        else:
            st.error("⚠️ Both fields are required!")

# --- Login Page ---
elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")

    login_pass = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if login_pass == "admin123":
            failed_attempts = 0
            st.success("✅ Reauthorized successfully! Redirecting to Retrieve Data...")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect password!")
