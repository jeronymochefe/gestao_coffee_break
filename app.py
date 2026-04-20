import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Coffee Break", page_icon="☕")

# --- 1. SEUS LINKS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTMOSKTetwvvzGCNkJJYbsEnVnlCKMTQbc8s6jY1va6Ot7OR0XcSjq3BcejF3AXYh7QCsrPQO1FKgev/pubhtml"
URL_SCRIPT_GOOGLE = "https://script.google.com/macros/s/AKfycbwq6aVdnMVSGt9UmTWgcsCT27WaHxokfW2bV3A5Ojr3Y2ECD3DvGT8wwlwTTuJzVmSh/exec"

# --- 2. CONTROLE DE ACESSO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #5D4037;'>☕ Coffee Break</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha do Caixa", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp {background-color: #FFF0F5;}
    .stButton>button {background-color: #FFB6C1; width: 100%; border-radius: 10px; color: #5D4037; font-weight: bold;}
    .saldo-container { text-align: center; padding: 20px; background-color: #ffffff; border-radius: 15px; border: 2px solid #FFB6C1; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("☕ CAIXA COFFEE BREAK")

# --- 4. LEITURA DOS DADOS (VERSÃO BLINDADA) ---
try:
    # Converte link de edição para link de exportação de dados
    csv_url = URL_PLANILHA.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit', '/export?format=csv')
    df_atual = pd.read_csv(csv_url)
    
    # Se a planilha não estiver vazia, limpa os nomes das colunas
    if not df_atual.empty:
        # Remove espaços e padroniza para evitar o erro 'Valor'
        df_atual.columns = [str(c).strip().capitalize() for c in df_atual.columns]
        
        # Corrige especificamente a coluna Descrição se estiver sem acento
        df_atual.rename(columns={'Descricao': 'Descrição'}, inplace=True)
        
        # Garante que a coluna 'Valor' é numérica
        if 'Valor' in df_atual.columns:
            df_atual['Valor'] = pd.to_numeric(df_atual['Valor'], errors='coerce').fillna(0)
    else:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

# --- 5. CÁLCULO DE SALDO ---
# Verifica se as colunas existem antes de somar
if 'Tipo' in df_atual.columns and 'Valor' in df_atual.columns:
    entradas = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
    saldo_total = entradas - saidas
else:
    saldo_total = 0.0

st.markdown(f"""
    <div class="saldo-container">
        <p style="margin:0; color: #5D4037; font-weight: bold;">SALDO ATUAL EM CAIXA</p>
        <h1 style="margin:0; color: #5D4037;">R$ {saldo_total:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# --- 6. FORMULÁRIO DE REGISTRO ---
with st.form("registro_caixa", clear_on_submit=True):
    st.subheader("Novo Registro")
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    forma = st.selectbox("Forma", ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito"])
    tipo = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
    submit = st.form_submit_button("REGISTRAR NO CAIXA")

if submit:
    if desc == "" or valor == 0:
        st.warning("Preencha os campos corretamente!")
    else:
        dados_envio = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "descricao": desc,
            "tipo": tipo,
            "forma": forma,
            "valor": valor
        }
        try:
            response = requests.post(URL_SCRIPT_GOOGLE, json=dados_envio)
            if response.status_code == 200:
                st.success("✅ Salvo com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao salvar no Google Script.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

# --- 7. HISTÓRICO ---
st.subheader("Últimas Movimentações")
st.dataframe(df_atual.iloc[::-1], use_container_width=True, hide_index=True)

# --- 8. PDF ---
def gerar_pdf(df_print, titulo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, titulo, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Data", 1); pdf.cell(70, 10, "Desc", 1); pdf.cell(30, 10, "Tipo", 1); pdf.cell(50, 10, "Valor", 1); pdf.ln()
    pdf.set_font("Arial", "", 10)
    for _, r in df_print.iterrows():
        pdf.cell(40, 10, str(r.get('Data', ''))[:10], 1)
        pdf.cell(70, 10, str(r.get('Descrição', ''))[:25], 1)
        pdf.cell(30, 10, str(r.get('Tipo', '')), 1)
        pdf.cell(50, 10, f"R$ {r.get('Valor', 0):.2f}", 1); pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

st.markdown("---")
if st.button("Gerar Relatório PDF"):
    if not df_atual.empty:
        pdf_bytes = gerar_pdf(df_atual, "FECHAMENTO DE CAIXA")
        st.download_button("Clique aqui para Baixar", data=pdf_bytes, file_name="caixa.pdf", mime="application/pdf")
    else:
        st.warning("Não há dados para gerar o PDF.")
