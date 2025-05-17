import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_connection

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Cambia esta clave por una segura

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

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reservas (nombre, servicio, fecha)
            VALUES (%s, %s, %s)
        ''', (nombre, servicio, fecha))
        conn.commit()
        cursor.close()
        conn.close()

        return f"<h2>Gracias, {nombre}. Tu cita para '{servicio}' fue agendada para el {fecha}.</h2><a href='/'>Volver al inicio</a>"

    return render_template('reservar.html', nombre=session.get('nombre'))

# Ruta unificada para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE correo = %s AND contrasena = %s', (correo, contrasena))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            session['usuario'] = usuario['id']
            session['rol'] = usuario['rol']
            session['nombre'] = usuario['nombre']
            if usuario['rol'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/cliente')
        else:
            flash('Credenciales inválidas')
            return redirect('/login')

    return render_template('login.html')

# Panel de administrador
@app.route('/admin')
def admin():
    if 'usuario' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM reservas')
    reservas = cursor.fetchall()
    cursor.close()
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

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reservas WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Registro de usuarios con WhatsApp
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        whatsapp = request.form['whatsapp']

        conn = get_connection()
        cursor = conn.cursor()

        # Insertar usuario
        cursor.execute('INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)',
                       (nombre, correo, contrasena, 'cliente'))
        usuario_id = cursor.lastrowid

        # Insertar WhatsApp en tabla clientes
        cursor.execute('INSERT INTO clientes (usuario_id, whatsapp) VALUES (%s, %s)', (usuario_id, whatsapp))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registro exitoso, por favor inicia sesión.')
        return redirect('/login')

    return render_template('registro.html')


if __name__ == '__main__':
    app.run(debug=True)
