from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    conn = sqlite3.connect('db/contacts.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('db/contacts.db'):
        os.makedirs('db', exist_ok=True)
        conn = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))
        conn.commit()
        conn.close()

init_db()

@app.route('/')
def home():
    logging.debug("Accessed home route")
    if not session.get('logged_in'):
        logging.debug("User not logged in, redirecting to login")
        return redirect(url_for('login'))
    logging.debug("User logged in, redirecting to index")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
        logging.debug(f"Attempting login with username: {username}")
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            logging.debug(f"Login successful for user: {username}")
            flash('You were successfully logged in', 'success')
            return redirect(url_for('index'))
        else:
            logging.debug(f"Login failed for user: {username}")
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        work = request.form['work']
        address = request.form['address']
        conn = get_db_connection()
        conn.execute('INSERT INTO contacts (name, email, phone, work, address) VALUES (?, ?, ?, ?, ?)',
                     (name, email, phone, work, address))
        conn.commit()
        conn.close()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_contact.html')

@app.route('/view_contacts')
def view_contacts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()
    return render_template('view_contacts.html', contacts=contacts)

@app.route('/modify_contact/<int:id>', methods=['GET', 'POST'])
def modify_contact(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        work = request.form['work']
        address = request.form['address']
        conn.execute('UPDATE contacts SET name=?, email=?, phone=?, work=?, address=? WHERE id=?',
                     (name, email, phone, work, address, id))
        conn.commit()
        conn.close()
        flash('Contact modified successfully!', 'success')
        return redirect(url_for('view_contacts'))
    conn.close()
    return render_template('modify_contact.html', contact=contact)

@app.route('/delete_contact/<int:id>', methods=['POST'])
def delete_contact(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
