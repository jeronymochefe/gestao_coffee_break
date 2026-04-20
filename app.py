# --- 4. LEITURA DOS DADOS (CORRIGIDO) ---
try:
    # Extrai o ID da planilha automaticamente para gerar o link de exportação CSV
    sheet_id = URL_PLANILHA.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    # Lê os dados ignorando o cache do navegador
    df_atual = pd.read_csv(csv_url)
    
    # Limpa espaços em branco nos nomes das colunas
    df_atual.columns = [c.strip() for c in df_atual.columns]
    
    # Converte valor para número (importante para o saldo)
    df_atual['Valor'] = pd.to_numeric(df_atual['Valor'], errors='coerce').fillna(0)
except Exception as e:
    # Mostra o erro na tela se falhar (ajuda a descobrir o que houve)
    st.error(f"Erro ao carregar dados: {e}")
    df_atual = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Forma", "Valor"])
