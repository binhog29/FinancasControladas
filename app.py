import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db_connection

# --- Configuração da Aplicação Flask ---
app = Flask(__name__)
# MUITO IMPORTANTE: Mude esta chave secreta para uma string aleatória e complexa!
# Ela é usada para proteger as sessões do usuário e as mensagens flash.
# Ex: use secrets.token_hex(16) no Python para gerar uma.
app.secret_key = 'sua_chave_secreta_aqui_troque_isso_por_algo_complexo_e_aleatorio!!!'

# --- Inicialização do Banco de Dados ---
# Este bloco é executado quando o app.py é carregado.
# Ele garante que o arquivo do banco de dados e as tabelas sejam criadas
# antes que o servidor comece a aceitar requisições.
with app.app_context():
    if not os.path.exists('financascontroladas.db'):
        print("Arquivo do banco de dados 'financascontroladas.db' não encontrado. Inicializando...")
        init_db()
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Arquivo do banco de dados 'financascontroladas.db' já existe. Pulando inicialização.")

# --- Contexto Global para Templates ---
# Esta função roda ANTES de CADA requisição para carregar os dados do usuário logado
# e torná-los acessíveis globalmente nos templates via 'g.user'.
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        # Busca o usuário pelo ID da sessão
        g.user = conn.execute(
            'SELECT id, username, email FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        conn.close()

# Adiciona o objeto 'now' (data/hora atual) ao contexto de todos os templates.
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    # Verifica se o usuário está logado para exibir informações personalizadas
    if g.user: # Usamos g.user agora que ele é carregado em before_request
        conn = get_db_connection()
        user_id = g.user['id']

        # Lógica para exibir o saldo total
        transactions = conn.execute(
            'SELECT amount, type FROM transactions WHERE user_id = ?', (user_id,)
        ).fetchall()

        total_balance = 0.0
        for t in transactions:
            if t['type'] == 'receita':
                total_balance += t['amount']
            else: # 'despesa'
                total_balance -= t['amount']

        conn.close()
        return render_template('index.html', total_balance=total_balance)
    else:
        # Se não estiver logado, mostra a página inicial padrão
        return render_template('index.html')

# --- Rota de Registro de Usuários ---
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        if not username:
            error = 'Nome de usuário é obrigatório.'
        elif not password:
            error = 'Senha é obrigatória.'
        elif not email:
            error = 'E-mail é obrigatório.'

        if error is None:
            conn = get_db_connection()
            try:
                # Gera o hash da senha antes de armazenar
                hashed_password = generate_password_hash(password)
                conn.execute(
                    "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                    (username, hashed_password, email)
                )
                conn.commit()
                flash('Registro bem-sucedido! Por favor, faça login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Nome de usuário ou e-mail já existe.'
            finally:
                conn.close()

        flash(error, 'danger') # Exibe a mensagem de erro
    return render_template('register.html')

# --- Rota de Login de Usuários ---
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        if user is None:
            error = 'Nome de usuário incorreto.'
        # Verifica a senha usando o hash
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id'] # Armazena o ID do usuário na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))

        flash(error, 'danger')
    return render_template('login.html')

# --- Rota de Logout ---
@app.route('/logout')
def logout():
    session.clear() # Limpa todos os dados da sessão
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# --- Rota para Adicionar Transações ---
@app.route('/add_transaction', methods=('GET', 'POST'))
def add_transaction():
    # Redireciona se o usuário não estiver logado
    if g.user is None:
        flash('Você precisa estar logado para adicionar transações.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Busca todas as categorias para preencher o dropdown no formulário
    categories = conn.execute('SELECT id, name, type FROM categories').fetchall()
    conn.close()

    # Define a data atual para pré-preencher o campo de data no formulário (GET)
    today_date = datetime.date.today().isoformat()

    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        transaction_type = request.form['type'] # 'receita' ou 'despesa'
        category_id = request.form['category_id'] # Pode vir como string, mas SQLite lida com INTEGER
        date = request.form['date'] # Espera formato 'YYYY-MM-DD'

        error = None

        # Validações básicas do formulário
        if not amount or not transaction_type or not date:
            error = 'Valor, tipo e data são obrigatórios.'
        try:
            amount = float(amount)
            if amount <= 0:
                error = 'O valor deve ser um número positivo.'
        except ValueError:
            error = 'O valor deve ser um número válido.'
        
        # Garante que category_id é None se for string vazia
        if not category_id or category_id == 'None': # 'None' pode vir se o valor padrão for selecionado
            category_id = None
        else:
            try:
                category_id = int(category_id)
            except ValueError:
                error = 'Categoria inválida.'


        if error is None:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO transactions (user_id, description, amount, type, category_id, date) VALUES (?, ?, ?, ?, ?, ?)',
                    (g.user['id'], description, amount, transaction_type, category_id, date)
                )
                conn.commit()
                flash(f'Transação de {transaction_type} adicionada com sucesso!', 'success')
                return redirect(url_for('index')) # Redireciona para a página principal após adicionar
            except Exception as e: # Captura erros gerais do DB
                error = f'Erro ao adicionar transação: {e}'
            finally:
                conn.close()
        
        flash(error, 'danger')

    return render_template('add_transaction.html', categories=categories, today=today_date)


# --- Rota para Visualizar Transações ---
@app.route('/view_transactions')
def view_transactions():
    # Redireciona se o usuário não estiver logado
    if g.user is None:
        flash('Você precisa estar logado para ver as transações.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_id = g.user['id']
    
    # Busca transações do usuário, juntando com o nome da categoria.
    # Ordena pela data mais recente primeiro.
    transactions = conn.execute(
        '''SELECT t.id, t.description, t.amount, t.type, t.date, c.name as category_name
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ?
           ORDER BY t.date DESC''',
        (user_id,)
    ).fetchall()
    
    conn.close()
    return render_template('view_transactions.html', transactions=transactions)


# --- Execução da Aplicação ---
if __name__ == '__main__':
    # Quando o script é executado diretamente, o Flask inicia o servidor de desenvolvimento.
    # O 'debug=True' permite o recarregamento automático do servidor em caso de mudanças no código
    # e fornece informações de depuração úteis. Desligue-o em produção.
    app.run(debug=True)