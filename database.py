import sqlite3
from datetime import datetime

def get_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        # Products table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cost_price REAL NOT NULL,
                sale_price REAL NOT NULL,
                quantity INTEGER DEFAULT 0
            )
        ''')
        # Transactions table (Entry/Exit)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                type TEXT CHECK(type IN ('IN', 'OUT')),
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                total_value REAL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        conn.commit()

def add_product(name, cost_price, sale_price):
    with get_connection() as conn:
        conn.execute(
            'INSERT INTO products (name, cost_price, sale_price, quantity) VALUES (?, ?, ?, 0)',
            (name, cost_price, sale_price)
        )
        conn.commit()

def get_all_products():
    with get_connection() as conn:
        return conn.execute('SELECT * FROM products').fetchall()

def update_stock(product_id, quantity, trans_type):
    with get_connection() as conn:
        # Update product quantity
        if trans_type == 'IN':
            conn.execute('UPDATE products SET quantity = quantity + ? WHERE id = ?', (quantity, product_id))
        else:
            conn.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))

        # Get sale price for financial record
        product = conn.execute('SELECT sale_price FROM products WHERE id = ?', (product_id,)).fetchone()
        total_value = product['sale_price'] * quantity if trans_type == 'OUT' else 0

        # Record transaction
        conn.execute(
            'INSERT INTO transactions (product_id, type, quantity, date, total_value) VALUES (?, ?, ?, ?, ?)',
            (product_id, trans_type, quantity, datetime.now().date(), total_value)
        )
        conn.commit()

def get_financial_report(start_date, end_date):
    with get_connection() as conn:
        query = '''
            SELECT p.name, SUM(t.quantity) as qty_sold, SUM(t.total_value) as total_revenue
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            WHERE t.type = 'OUT' AND t.date BETWEEN ? AND ?
            GROUP BY p.id
        '''
        return conn.execute(query, (start_date, end_date)).fetchall()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
