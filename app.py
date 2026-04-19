import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA SENHA ---
SENHA_CORRETA = "1234" # ALTERE AQUI PARA A SUA SENHA

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center; color: #5D4037;'>☕ Coffee Break</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if pwd == SENHA_CORRETA:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

if check_password():
    st.set_page_config(page_title="Coffee Break", page_icon="☕")
    
    # CSS Customizado para iPhone (Rosa)
    st.markdown("""
        <style>
        .stApp { background-color: #FFF0F5; }
        .stButton>button { background-color: #FFB6C1; border-radius: 10px; color: #5D4037; font-weight: bold; height: 3em; }
        div[data-baseweb="select"] > div { background-color: white; }
        </style>
        """, unsafe_allow_html=True)

    st.title("☕ CAIXA COFFEE BREAK")

    # Registro de Movimentação
    with st.container():
        st.markdown("### ➕ Nova Entrada/Saída")
        desc = st.text_input("Descrição (ex: Café Expresso)")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        forma = st.selectbox("Forma", ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito"])
        tipo = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
        
        if st.button("REGISTRAR"):
            st.success(f"Registrado com sucesso: {desc}")
            # DICA: Para salvar de verdade no iPhone, o ideal é conectar ao Google Sheets nas 'Secrets' do Streamlit

    # Fechamentos (Simulação visual para Mobile)
    st.markdown("---")
    st.markdown("### 📊 Relatórios")
    col1, col2 = st.columns(2)
    with col1:
        st.button("📄 PDF do Dia")
    with col2:
        st.button("📅 PDF do Mês")

    if st.sidebar.button("Bloquear Sistema"):
        st.session_state["password_correct"] = False
        st.rerun()
