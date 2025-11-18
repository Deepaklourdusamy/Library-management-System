from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'change_this_in_prod'

def get_db():
    # returns a new connection (caller must close)
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# BOOKS CRUD
@app.route('/books')
def books():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, author, category, copies FROM books ORDER BY id DESC')
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    category = request.form.get('category')
    copies = request.form.get('copies') or 1
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO books (title, author, category, copies) VALUES (%s,%s,%s,%s)',
                (title, author, category, copies))
    conn.commit()
    cur.close()
    conn.close()
    flash('Book added', 'success')
    return redirect(url_for('books'))

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM books WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Book deleted', 'warning')
    return redirect(url_for('books'))

# MEMBERS CRUD
@app.route('/members')
def members():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email, contact FROM members ORDER BY id DESC')
    members = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['POST'])
def add_member():
    name = request.form.get('name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO members (name,email,contact) VALUES (%s,%s,%s)', (name,email,contact))
    conn.commit()
    cur.close()
    conn.close()
    flash('Member added', 'success')
    return redirect(url_for('members'))

# ISSUE BOOK
@app.route('/issue')
def issue():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, copies FROM books WHERE copies>0')
    books = cur.fetchall()
    cur.execute('SELECT id, name FROM members')
    members = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('issue.html', books=books, members=members)

@app.route('/issue_book', methods=['POST'])
def issue_book():
    book_id = request.form.get('book')
    member_id = request.form.get('member')
    date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO issues (book_id, member_id, issue_date) VALUES (%s,%s,%s)',
                (book_id, member_id, date))
    cur.execute('UPDATE books SET copies = copies - 1 WHERE id=%s', (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Book issued', 'success')
    return redirect(url_for('view_issues'))

@app.route('/view_issues')
def view_issues():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT i.id, b.title, m.name, i.issue_date, i.return_date, i.fine
                FROM issues i
                LEFT JOIN books b ON i.book_id=b.id
                LEFT JOIN members m ON i.member_id=m.id
                ORDER BY i.id DESC""")
    issues = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_issues.html', issues=issues)

@app.route('/return/<int:id>', methods=['POST'])
def return_book(id):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE issues SET return_date=%s WHERE id=%s', (today,id))
    # optional: calculate fine logic here
    cur.execute('SELECT book_id FROM issues WHERE id=%s', (id,))
    row = cur.fetchone()
    if row:
        book_id = row[0]
        cur.execute('UPDATE books SET copies = copies + 1 WHERE id=%s', (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Book returned', 'info')
    return redirect(url_for('view_issues'))

if __name__ == '__main__':
    app.run(debug=True)
