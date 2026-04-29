from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from analyzer import categorize_transactions, load_to_postgres
import os

app = Flask(__name__)

# Configuração de conexão com o banco local via Docker
DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/financas_mvp"

@app.route('/', methods=['GET'])
def index():
    """Renderiza a página inicial com o formulário de upload."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recebe o CSV, processa via Pandas e salva no Postgres."""
    if 'file' not in request.files:
        return "Nenhum arquivo enviado.", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado.", 400

    if file and file.filename.endswith('.csv'):
        # 1. Lê o CSV enviado pelo usuário direto para o Pandas (em memória)
        df = pd.read_csv(file)
        
        # 2. Passa pela regra de negócio (já testada via TDD)
        df_categorizado = categorize_transactions(df)
        
        # 3. Salva no banco de dados
        load_to_postgres(df_categorizado, DATABASE_URL, "extrato_flask")
        
        # 4. Cria um resumo para exibir na tela
        resumo = df_categorizado.groupby('categoria')['valor'].sum().reset_index()
        
        # Converte o resumo para HTML para renderizar fácil no template
        tabela_html = resumo.to_html(classes='table table-striped', index=False)
        
        return render_template('result.html', tabela=tabela_html)
    else:
        return "Por favor, envie um arquivo .csv válido.", 400

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True, port=5000)