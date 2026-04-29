import pandas as pd
from analyzer import categorize_transactions

def test_categorize_transactions():
    # 1. Arrange: Preparação dos dados simulando o CSV do banco
    dados_mock = {
        'data': ['2026-04-01', '2026-04-02', '2026-04-03', '2026-04-04'],
        'descricao': ['SALARIO EMPRESA', 'MERCADO ATACADAO', 'NETFLIX', 'COMPRA IFOOD'],
        'valor': [5000.00, -350.50, -39.90, -50.00]
    }
    df = pd.DataFrame(dados_mock)

    # 2. Act: Execução da função que será implementada
    df_resultado = categorize_transactions(df)

    # 3. Assert: Verificação dos resultados esperados
    # Verifica se as categorias foram aplicadas corretamente
    assert df_resultado.loc[df_resultado['descricao'] == 'SALARIO EMPRESA', 'categoria'].iloc[0] == 'Entrada'
    assert df_resultado.loc[df_resultado['descricao'] == 'MERCADO ATACADAO', 'categoria'].iloc[0] == 'Mercado'
    assert df_resultado.loc[df_resultado['descricao'] == 'NETFLIX', 'categoria'].iloc[0] == 'Streaming'
    assert df_resultado.loc[df_resultado['descricao'] == 'COMPRA IFOOD', 'categoria'].iloc[0] == 'Outros'

    # Verifica a totalização de entradas e saídas (Validação de integridade)
    entradas = df_resultado[df_resultado['valor'] > 0]['valor'].sum()
    saidas = df_resultado[df_resultado['valor'] < 0]['valor'].sum()
    
    assert entradas == 5000.00
    assert saidas == -440.40