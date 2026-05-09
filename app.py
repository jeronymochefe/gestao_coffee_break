import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Coffee Break", page_icon="☕", layout="centered")

# --- AUTENTICAÇÃO ---
if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Acesso Restrito")
    senha = st.text_input("Senha do Caixa", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- TÍTULO E CONEXÃO ---
st.title("☕ CAIXA COFFEE BREAK")
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # ttl=0 garante que os dados venham atualizados do Google Sheets
        df = conn.read(ttl=0)
        # Limpeza e padronização das colunas
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar na planilha: {e}")
        return pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

df_atual = carregar_dados()

# --- RESUMO FINANCEIRO ---
entradas = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
saidas = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
saldo_total = entradas - saidas

st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 15px; border: 2px solid #5D4037; margin-bottom: 25px;">
        
