import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

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

def gerar_pdf(df_filtrado, titulo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, f"Relatorio: {titulo}", ln=True, align="C")
    pdf.ln(10)
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 10, "Data", 1)
    pdf.cell(75, 10, "Descricao", 1)
    pdf.cell(30, 10, "Tipo", 1)
    pdf.cell(50, 10, "Valor", 1)
    pdf.ln()
    
    # Linhas
    pdf.set_font("Arial", "", 10)
    for _, row in df_filtrado.iterrows():
        pdf.cell(35, 10, str(row['Data'])[:10], 1)
        pdf.cell(75, 10, str(row['Descrição'])[:30], 1)
        pdf.cell(30, 10, str(row['Tipo']), 1)
        pdf.cell(50, 10, f"R$ {float(row['Valor']):.2f}", 1)
        pdf.ln()
    
    # Totais
    ent = df_filtrado[df_filtrado["Tipo"] == "Entrada"]["Valor"].sum()
    sai = df_filtrado[df_filtrado["Tipo"] == "Saída"]["Valor"].sum()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"Total Entradas: R$ {ent:.2f}", ln=True)
    pdf.cell(190, 10, f"Total Saidas: R$ {sai:.2f}", ln=True)
    pdf.cell(190, 10, f"Saldo Final: R$ {ent - sai:.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

if check_password():
    st.markdown("""
        <style>
        .stApp {background-color: #FFF0F5;}
        .stButton>button {background-color: #FFB6C1; width: 100%; border-radius: 10px; color: #5D4037; font-weight: bold;}
        .saldo-container { text-align: center; padding: 20px; background-color: #ffffff; border-radius: 15px; border: 2px solid #FFB6C1; margin-bottom: 25px; }
        [data-testid="stDataTableColumnHeaderCellSelectAll"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.title("☕ CAIXA COFFEE BREAK")

    conn = st.connection("gsheets", type=GSheetsConnection)
    
    try:
        df_atual = conn.read()
        df_atual['Valor'] = pd.to_numeric(df_atual['Valor'], errors='coerce').fillna(0)
    except:
        df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])

    # LÓGICA DE SALDO
    entradas = df_atual[df_atual["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df_atual[df_atual["Tipo"] == "Saída"]["Valor"].sum()
    saldo_total = entradas - saidas

    st.markdown(f"""
        <div class="saldo-container">
            <p style="margin:0; color: #5D4037; font-weight: bold;">SALDO ATUAL EM CAIXA</p>
            <h1 style="margin:0; color: #5D4037;">R$ {saldo_total:.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

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
            nova_linha = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Descrição": desc, "Tipo": tipo, "Forma": forma, "Valor": valor}])
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(data=df_final)
            st.success("✅ Registrado!")
            st.rerun()

    st.subheader("Últimas Movimentações")
    st.dataframe(df_atual.iloc[::-1], use_container_width=True, hide_index=True)

    # --- BOTÕES DE FECHAMENTO (PDF) ---
    st.markdown("---")
    st.subheader("📄 Baixar Fechamento")
    col_dia, col_mes = st.columns(2)

    # Preparar dados para PDF
    df_atual['Data_DT'] = pd.to_datetime(df_atual['Data'], dayfirst=True, errors='coerce')
    hoje = datetime.now().date()
    mes_atual = hoje.month

    with col_dia:
        df_dia = df_atual[df_atual['Data_DT'].dt.date == hoje]
        if not df_dia.empty:
            pdf_d = gerar_pdf(df_dia, f"DIA {hoje.strftime('%d/%m/%Y')}")
            st.download_button("PDF DO DIA", data=pdf_d, file_name=f"fechamento_dia_{hoje}.pdf", mime="application/pdf")
        else:
            st.info("Sem vendas hoje.")

    with col_mes:
        df_mes = df_atual[df_atual['Data_DT'].dt.month == mes_atual]
        if not df_mes.empty:
            pdf_m = gerar_pdf(df_mes, f"MES {datetime.now().strftime('%m/%Y')}")
            st.download_button("PDF DO MÊS", data=pdf_m, file_name=f"fechamento_mes_{datetime.now().strftime('%m_%Y')}.pdf", mime="application/pdf")
        else:
            st.info("Sem vendas este mês.")
