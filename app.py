import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Coffee Break", page_icon="☕")

# Senha de Acesso
SENHA_CORRETA = "1234"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='color: #5D4037; text-align: center;'>☕ Coffee Break</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if pwd == SENHA_CORRETA:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

if check_password():
    # CSS Customizado - Removido os balões brancos e ajustado layout
    st.markdown("""
        <style>
        .stApp {background-color: #FFF0F5;}
        .stButton>button {background-color: #FFB6C1; width: 100%; border-radius: 10px; color: #5D4037; font-weight: bold;}
        /* Estilização do Saldo Centralizado */
        .saldo-container {
            text-align: center;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 15px;
            border: 2px solid #FFB6C1;
            margin-bottom: 25px;
        }
        [data-testid="stDataTableColumnHeaderCellSelectAll"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.title("☕ CAIXA COFFEE BREAK")

    # Conexão com Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    try:
        df_atual = conn.read()
    except:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

    if df_atual.empty:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

    # --- LÓGICA DE SALDO ---
    entradas = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
    saldo_total = entradas - saidas

    # Exibição do Saldo Centralizado e Limpo
    st.markdown(f"""
        <div class="saldo-container">
            <p style="margin:0; color: #5D4037; font-weight: bold;">SALDO ATUAL EM CAIXA</p>
            <h1 style="margin:0; color: #5D4037;">R$ {saldo_total:.2f}</h1>
            <small style="color: #888;">O saldo de ontem é o inicial de hoje automaticamente.</small>
        </div>
    """, unsafe_allow_html=True)

    # --- FORMULÁRIO DE REGISTRO ---
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Novo Registro")
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        forma = st.selectbox("Forma", ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito"])
        tipo = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
        submit = st.form_submit_button("REGISTRAR NO CAIXA")

    if submit:
        if desc == "" or valor == 0:
            st.warning("Preencha a descrição e o valor!")
        else:
            nova_linha = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Descrição": desc,
                "Tipo": tipo,
                "Forma": forma,
                "Valor": valor
            }])
            
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(data=df_final)
            st.success("✅ Registrado!")
            st.rerun()

    # --- HISTÓRICO FIXO ---
    st.subheader("Últimas Movimentações")
    st.dataframe(
        df_atual.iloc[::-1], 
        use_container_width=True, 
        hide_index=True
    )
