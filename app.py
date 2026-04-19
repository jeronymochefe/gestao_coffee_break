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
    # CSS Customizado (Rosa e Marrom)
    st.markdown("""
        <style>
        .stApp {background-color: #FFF0F5;}
        .stButton>button {background-color: #FFB6C1; width: 100%; border-radius: 10px; color: #5D4037; font-weight: bold;}
        .metric-container {background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #FFB6C1; margin-bottom: 20px;}
        </style>
    """, unsafe_allow_html=True)

    st.title("☕ CAIXA COFFEE BREAK")

    # Conexão com Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tenta ler os dados, se der erro ou estiver vazio, cria DataFrame vazio
    try:
        df_atual = conn.read()
    except:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

    if df_atual.empty:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

    # --- LÓGICA DE SALDO PERSISTENTE ---
    # Soma todas as entradas e subtrai todas as saídas registradas até hoje
    entradas_totais = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
    saidas_totais = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
    saldo_total_acumulado = entradas_totais - saidas_totais

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        # Campo para ajuste manual (caso falte ou sobre dinheiro fisicamente)
        ajuste = st.number_input("Ajuste Manual de Caixa (+/-)", value=0.0, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        saldo_exibido = saldo_total_acumulado + ajuste
        st.metric("Saldo Atual em Caixa", f"R$ {saldo_exibido:.2f}")
        st.caption("O saldo de ontem é o inicial de hoje automaticamente.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- FORMULÁRIO DE REGISTRO ---
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Novo Registro")
        desc = st.text_input("Descrição (Ex: Venda Café, Compra Leite)")
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
            st.success(f"✅ {tipo} de R$ {valor:.2f} registrada!")
            st.rerun()

    # --- VISUALIZAÇÃO ---
    if st.checkbox("Ver histórico de movimentações"):
        # Mostra as mais recentes primeiro
        st.dataframe(df_atual.iloc[::-1], use_container_width=True)
