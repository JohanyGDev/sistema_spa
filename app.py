from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

# Inicialización de la app Flask
app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Clave para manejar sesiones

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('spa.db')
    c = conn.cursor()

    # Tabla de reservas
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            servicio TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')

    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # Insertar un administrador por defecto si no existe
    c.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (nombre, usuario, contrasena, rol) VALUES (?, ?, ?, ?)",
                  ('Administrador', 'admin', 'admin123', 'admin'))

    conn.commit()
    conn.close()

# Ejecutar inicialización
init_db()

# Ruta principal
@app.route('/')
def home():
    return render_template('home.html')


# Página de servicios
@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

# Página para reservar cita
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if 'usuario' not in session or session.get('rol') != 'cliente':
        flash('Debes iniciar sesión para agendar una cita.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = session.get('nombre')
        servicio = request.form['servicio']
        fecha = request.form['fecha']

        conn = sqlite3.connect('spa.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reservas (nombre, servicio, fecha)
            VALUES (?, ?, ?)
        ''', (nombre, servicio, fecha))
        conn.commit()
        conn.close()

        return f"<h2>Gracias, {nombre}. Tu cita para '{servicio}' fue agendada para el {fecha}.</h2><a href='/'>Volver al inicio</a>"

    # Si es GET, mostrar el formulario de reserva
    return render_template('reservar.html', nombre=session.get('nombre'))

# Ruta unificada para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = sqlite3.connect('spa.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?', (usuario, contrasena))
        user = c.fetchone()
        conn.close()

        if user:
            session['usuario'] = user[2]  # usuario
            session['rol'] = user[4]      # rol

            if session['rol'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('cliente_dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')

# Panel de administrador
@app.route('/admin')
def admin():
    if 'usuario' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    c.execute('SELECT * FROM reservas')
    reservas = c.fetchall()
    conn.close()

    return render_template('admin.html', reservas=reservas)

# Panel del cliente
@app.route('/cliente')
def cliente_dashboard():
    if 'usuario' not in session or session['rol'] != 'cliente':
        return redirect(url_for('login'))

    return render_template('cliente_dashboard.html')

# Eliminar reserva (solo para admin)
@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 'usuario' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    c.execute('DELETE FROM reservas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)
