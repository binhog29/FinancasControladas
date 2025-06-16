import sqlite3
import datetime

DATABASE = 'financascontroladas.db'

def get_db_connection():
    """
    Função para obter uma conexão com o banco de dados.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acessar colunas como dicionários (ex: row['name'])
    return conn

def init_db():
    """
    Função para inicializar o banco de dados e criar as tabelas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, -- Lembre-se: armazenar HASH da senha, NUNCA texto puro!
            email TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL -- 'receita' ou 'despesa'
        )
    ''')

    # Populando categorias padrão (se não existirem)
    initial_categories = [
        ('Salário', 'receita'),
        ('Investimentos', 'receita'),
        ('Venda', 'receita'),
        ('Outras Receitas', 'receita'),
        ('Alimentação', 'despesa'),
        ('Moradia', 'despesa'),
        ('Transporte', 'despesa'),
        ('Lazer', 'despesa'),
        ('Educação', 'despesa'),
        ('Saúde', 'despesa'),
        ('Compras', 'despesa'),
        ('Contas', 'despesa'),
        ('Outras Despesas', 'despesa'),
    ]
    for category_name, category_type in initial_categories:
        try:
            cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (category_name, category_type))
        except sqlite3.IntegrityError:
            pass # Se a categoria já existir (UNIQUE constraint), ignora o erro

    # Tabela de Contas Financeiras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,       -- Ex: "Conta Corrente", "Cartão de Crédito Nubank", "Dinheiro em Espécie"
            type TEXT NOT NULL,       -- Ex: 'banco', 'cartao_credito', 'cartao_debito', 'dinheiro'
            initial_balance REAL NOT NULL DEFAULT 0.0, -- Saldo inicial da conta
            current_balance REAL NOT NULL DEFAULT 0.0, -- Saldo atual da conta
            limit_amount REAL,        -- Para cartões de crédito, o limite
            due_day INTEGER,          -- Para cartões de crédito, dia de vencimento da fatura
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, name) -- Garante que um usuário não tenha duas contas com o mesmo nome
        )
    ''')

    # Tabela de Transações
    # Ela é CRIADA com o account_id já incluso.
    # A lógica de ALTER TABLE foi removida pois não é necessária
    # se o banco de dados é recriado ou se a tabela já é criada corretamente.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER, -- AGORA CADA TRANSAÇÃO ESTÁ LIGADA A UMA CONTA
            description TEXT,
            amount REAL NOT NULL,
            type TEXT NOT NULL, -- 'receita' ou 'despesa'
            category_id INTEGER,
            date TEXT NOT NULL, -- Formatoण्याच्या-MM-DD
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    ''')

    conn.commit()
    conn.close()

# Se este script for executado diretamente, ele inicializa o banco de dados
if __name__ == '__main__':
    init_db()
    print("Banco de dados 'financascontroladas.db' inicializado com sucesso!")