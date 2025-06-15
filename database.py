import sqlite3

DATABASE = 'financascontroladas.db'

def get_db_connection():
    """
    Função para obter uma conexão com o banco de dados.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acessar colunas como dicionários (ex: row['nome'])
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
            # Se a categoria já existir (UNIQUE constraint), ignora o erro
            pass

    # Tabela de Transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            type TEXT NOT NULL, -- 'receita' ou 'despesa'
            category_id INTEGER,
            date TEXT NOT NULL, -- Formato YYYY-MM-DD
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    conn.commit()
    conn.close()

# Se este script for executado diretamente, ele inicializa o banco de dados
if __name__ == '__main__':
    init_db()
    print("Banco de dados 'financascontroladas.db' inicializado com sucesso!")