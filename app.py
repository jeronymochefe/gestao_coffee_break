import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Coffee Break", page_icon="☕")

# Senha
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha do Caixa", type="password")
    if st.button("Entrar") and senha == "1234":
        st.session_state.auth = True
        st.rerun()
    st.stop()

st.title("☕ CAIXA COFFEE BREAK")

# --- CONEXÃO OFICIAL (USA AS SECRETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lê os dados de forma segura
    df_atual = conn.read(ttl=0)
    # Limpa nomes de colunas
    df_atual.columns = [str(c).strip().capitalize() for c in df_atual.columns]
    df_atual['Valor'] = pd.to_numeric(df_atual['Valor'], errors='coerce').fillna(0)
except:
    df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

# Cálculo de Saldo
entradas = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
saidas = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
saldo_total = entradas - saidas

st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #ffffff; border-radius: 15px; border: 2px solid #FFB6C1; margin-bottom: 25px;">
        <p style="margin:0; color: #5D4037; font-weight: bold;">SALDO ATUAL EM CAIXA</p>
        <h1 style="margin:0; color: #5D4037;">R$ {saldo_total:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# --- FORMULÁRIO ---
with st.form("registro", clear_on_submit=True):
    st.subheader("Novo Registro")
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    forma = st.selectbox("Forma", ["Dinheiro", "Pix", "Cartão"])
    tipo = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
    if st.form_submit_button("REGISTRAR"):
        nova_linha = pd.DataFrame([{
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Descrição": desc,
            "Tipo": tipo,
            "Forma": forma,
            "Valor": valor
        }])
        df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
        # O comando de salvar oficial é muito mais estável
        conn.update(data=df_final)
        st.success("✅ Salvo com sucesso!")
        st.rerun()

# --- HISTÓRICO ---
st.subheader("Últimas Movimentações")
st.dataframe(df_atual.iloc[::-1], use_container_width=True, hide_index=True)