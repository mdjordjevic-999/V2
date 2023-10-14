from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'geheimnisvollesgeheimnis'  # Geheimer Schlüssel für die Sitzungsverwaltung

# MySQL-Konfiguration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'abc123',
    'database': 'farben_db'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/')
def index():
    if 'username' in session:
        # Setze die Hintergrundfarbe basierend auf der Lieblingsfarbe des Benutzers
        style = f'background-color: {session["favorite_color"]};'
        return render_template('index.html', username=session['username'], favorite_color=session['favorite_color'], style=style)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        lieblingsfarbe = request.form['lieblingsfarbe']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Benutzername bereits vorhanden. Bitte wählen Sie einen anderen Benutzernamen."
        else:
            cursor.execute("INSERT INTO users (username, password, lieblingsfarbe) VALUES (%s, %s, %s)",
                           (username, password, lieblingsfarbe))
            conn.commit()
            return "Erfolgreich registriert!"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = username
            session['favorite_color'] = user[3]  # Hier sollte die Lieblingsfarbe aus der Datenbank kommen
            return redirect(url_for('index'))
        else:
            return "Falsche Anmeldeinformationen. Bitte versuchen Sie es erneut."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('favorite_color', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/set_color', methods=['POST'])
def set_color():
    if 'username' in session:
        new_color = request.form['new_color']
        cursor.execute("UPDATE users SET lieblingsfarbe = %s WHERE username = %s", (new_color, session['username']))
        conn.commit()
        session['favorite_color'] = new_color
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
