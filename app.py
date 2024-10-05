from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    words = conn.execute('SELECT * FROM words WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()

    if not words:
        return redirect(url_for('register'))

    return render_template('search_results.html', words=words)

@app.route('/word/<int:word_id>')
def word_detail(word_id):
    conn = get_db_connection()
    word = conn.execute('SELECT * FROM words WHERE id = ?', (word_id,)).fetchone()

    # 単語が登録されていない場合、登録ページにリダイレクト
    if word is None:
        return redirect(url_for('register'))

    comments = conn.execute('SELECT * FROM comments WHERE word_id = ?', (word_id,)).fetchall()
    conn.close()
    return render_template('word_detail.html', word=word, comments=comments)

@app.route('/word/<int:word_id>/comment', methods=['POST'])
def add_comment(word_id):
    user_comment = request.form['user_comment']  # フォームからの入力を取得
    conn = get_db_connection()
    conn.execute('INSERT INTO comments (word_id, user_comment) VALUES (?, ?)', (word_id, user_comment))
    conn.commit()
    conn.close()
    return redirect(url_for('word_detail', word_id=word_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        alias = request.form['alias']
        abbreviation = request.form['abbreviation']
        category = request.form['category']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('INSERT INTO words (name, alias, abbreviation, category, description) VALUES (?, ?, ?, ?, ?)',
                     (name, alias, abbreviation, category, description))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('register.html')

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            alias TEXT,
            abbreviation TEXT,
            category TEXT,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            word_id INTEGER,
            user_comment TEXT,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (word_id) REFERENCES words (id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # アプリケーションの起動時にデータベースを初期化
    app.run(debug=True)
