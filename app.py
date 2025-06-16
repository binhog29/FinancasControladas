import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db_connection

# --- Configuração da Aplicação Flask ---
app = Flask(__name__)
# MUITO IMPORTANTE: Mude esta chave secreta para uma string aleatória e complexa!
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

        # NOVO: Busca as contas do usuário
        accounts = conn.execute(
            'SELECT id, name, type, current_balance FROM accounts WHERE user_id = ?', (user_id,)
        ).fetchall()

        # Calcula o saldo total somando os current_balance das contas (se atualizado)
        total_balance = 0.0
        for account in accounts:
            total_balance += account['current_balance']

        conn.close()
        return render_template('index.html', total_balance=total_balance, accounts=accounts)
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

        flash(error, 'danger')
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
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))

        flash(error, 'danger')
    return render_template('login.html')

# --- Rota de Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# --- Rota: Adicionar Conta Financeira ---
@app.route('/add_account', methods=('GET', 'POST'))
def add_account():
    if g.user is None:
        flash('Você precisa estar logado para adicionar contas.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        account_type = request.form['type']
        initial_balance_str = request.form.get('initial_balance', '0.0')
        limit_amount_str = request.form.get('limit_amount', '')
        due_day_str = request.form.get('due_day', '')

        error = None
        initial_balance = 0.0
        limit_amount = None
        due_day = None

        if not name or not account_type:
            error = 'Nome e tipo da conta são obrigatórios.'

        try:
            initial_balance = float(initial_balance_str)
        except ValueError:
            error = 'Saldo inicial deve ser um número válido.'

        if limit_amount_str:
            try:
                limit_amount = float(limit_amount_str)
                if limit_amount < 0: error = 'Limite deve ser positivo.'
            except ValueError:
                error = 'Limite deve ser um número válido.'

        if due_day_str:
            try:
                due_day = int(due_day_str)
                if not (1 <= due_day <= 31): error = 'Dia de vencimento inválido (1-31).'
            except ValueError:
                error = 'Dia de vencimento deve ser um número inteiro.'

        if error is None:
            conn = get_db_connection()
            try:
                conn.execute(
                    "INSERT INTO accounts (user_id, name, type, initial_balance, current_balance, limit_amount, due_day) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (g.user['id'], name, account_type, initial_balance, initial_balance, limit_amount, due_day)
                )
                conn.commit()
                flash('Conta adicionada com sucesso!', 'success')
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                error = 'Você já tem uma conta com este nome.'
            except Exception as e:
                error = f'Erro ao adicionar conta: {e}'
            finally:
                conn.close()

        flash(error, 'danger')
    return render_template('add_account.html')

# --- Rota: Visualizar Contas Financeiras ---
@app.route('/view_accounts')
def view_accounts():
    if g.user is None:
        flash('Você precisa estar logado para ver suas contas.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    accounts = conn.execute(
        'SELECT id, name, type, initial_balance, current_balance, limit_amount, due_day FROM accounts WHERE user_id = ?',
        (g.user['id'],)
    ).fetchall()
    conn.close()
    return render_template('view_accounts.html', accounts=accounts)


# --- Rota: Adicionar Transações ---
@app.route('/add_transaction', methods=('GET', 'POST'))
def add_transaction():
    if g.user is None:
        flash('Você precisa estar logado para adicionar transações.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    categories = conn.execute('SELECT id, name, type FROM categories').fetchall()
    accounts = conn.execute('SELECT id, name, type FROM accounts WHERE user_id = ?', (g.user['id'],)).fetchall()
    conn.close()

    today_date = datetime.date.today().isoformat()

    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        transaction_type = request.form['type']
        category_id = request.form['category_id']
        account_id = request.form['account_id']
        date = request.form['date']

        error = None

        if not amount or not transaction_type or not date or not account_id:
            error = 'Valor, tipo, data e CONTA são obrigatórios.'
        try:
            amount = float(amount)
            if amount <= 0:
                error = 'O valor deve ser um número positivo.'
        except ValueError:
            error = 'O valor deve ser um número válido.'
        
        if not category_id or category_id == 'None':
            category_id = None
        else:
            try:
                category_id = int(category_id)
            except ValueError:
                error = 'Categoria inválida.'
        
        try:
            account_id = int(account_id)
        except ValueError:
            error = 'Conta inválida.'


        if error is None:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO transactions (user_id, account_id, description, amount, type, category_id, date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (g.user['id'], account_id, description, amount, transaction_type, category_id, date)
                )
                
                # Atualiza o current_balance da conta após a transação
                current_account_balance = conn.execute(
                    'SELECT current_balance FROM accounts WHERE id = ?', (account_id,)
                ).fetchone()['current_balance']

                if transaction_type == 'receita':
                    new_account_balance = current_account_balance + amount
                else: # 'despesa'
                    new_account_balance = current_account_balance - amount
                
                conn.execute(
                    'UPDATE accounts SET current_balance = ? WHERE id = ?', (new_account_balance, account_id)
                )

                conn.commit()
                flash(f'Transação de {transaction_type} adicionada com sucesso!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                error = f'Erro ao adicionar transação: {e}'
            finally:
                conn.close()
        
        flash(error, 'danger')

    return render_template('add_transaction.html', categories=categories, accounts=accounts, today=today_date)


# --- Rota: Visualizar Transações ---
@app.route('/view_transactions')
def view_transactions():
    if g.user is None:
        flash('Você precisa estar logado para ver suas transações.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_id = g.user['id']
    
    # Busca transações com o nome da categoria E O NOME DA CONTA
    transactions = conn.execute(
        '''SELECT t.id, t.description, t.amount, t.type, t.date, c.name as category_name, a.name as account_name
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           LEFT JOIN accounts a ON t.account_id = a.id
           WHERE t.user_id = ?
           ORDER BY t.date DESC''',
        (user_id,)
    ).fetchall()
    
    conn.close()
    return render_template('view_transactions.html', transactions=transactions)


# --- Execução da Aplicação ---
if __name__ == '__main__':
    app.run(debug=True)