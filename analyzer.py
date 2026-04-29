import pandas as pd
from sqlalchemy import create_engine

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função pura para categorizar o DataFrame. 
    Criada para satisfazer o test_categorize_transactions.
    """
    # Dicionário de regras mapeando palavras-chave para categorias
    regras = {
        'MERCADO': 'Mercado',
        'ATACADAO': 'Mercado',
        'CARREFOUR': 'Mercado',
        'NETFLIX': 'Streaming',
        'SPOTIFY': 'Streaming',
        'PRIME': 'Streaming'
    }

    def classificar(row):
        # Se o valor for positivo, é entrada de dinheiro
        if row['valor'] > 0:
            return 'Entrada'
        
        # Analisa a descrição para categorizar a saída
        descricao = str(row['descricao']).upper()
        for palavra_chave, categoria in regras.items():
            if palavra_chave in descricao:
                return categoria
                
        # Se não bater com nenhuma regra, cai na categoria genérica
        return 'Outros'

    # Aplica a regra linha a linha e cria a nova coluna
    df_processado = df.copy()
    df_processado['categoria'] = df_processado.apply(classificar, axis=1)
    
    return df_processado


def load_to_postgres(df: pd.DataFrame, db_url: str, table_name: str):
    """Carrega o DataFrame processado para o banco de dados PostgreSQL."""
    engine = create_engine(db_url)
    
    # if_exists='replace' recria a tabela. Para produção, 'append' seria melhor.
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"[+] Dados inseridos com sucesso na tabela '{table_name}'.")


if __name__ == "__main__":
    # URL de conexão com os dados definidos no docker-compose.yml
    DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/financas_mvp"

    # Em um cenário real, você leria do CSV do seu banco assim:
    # df_extrato = pd.read_csv('seu_extrato.csv')
    
    # Para o MVP rodar imediatamente, simulamos a leitura do CSV:
    dados_csv_simulado = {
        'data': ['2026-04-01', '2026-04-05', '2026-04-10', '2026-04-12'],
        'descricao': ['PIX RECEBIDO - JOAO', 'COMPRA CARREFOUR', 'ASSINATURA SPOTIFY', 'POSTO DE GASOLINA'],
        'valor': [1500.00, -420.00, -21.90, -200.00]
    }
    df_extrato = pd.DataFrame(dados_csv_simulado)

    print("[*] Processando transações...")
    df_final = categorize_transactions(df_extrato)
    
    print("\n--- Resumo Analítico ---")
    resumo = df_final.groupby('categoria')['valor'].sum().reset_index()
    print(resumo.to_string(index=False))
    print("------------------------\n")

    print("[*] Conectando ao PostgreSQL e exportando dados...")
    load_to_postgres(df_final, DATABASE_URL, "extrato_categorizado")