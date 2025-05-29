import hashlib
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_connection
from datetime import datetime, time, timedelta

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Cambia esta clave por una segura

# Context processor para usar `now()` en las plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Ruta principal
@app.route('/')
def home():
    return render_template('home.html')

# Página de servicios
@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

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

@app.route('/colaboradoras')
def colaboradoras():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM especialidades')
    especialidades = cursor.fetchall()

    cursor.execute('''
        SELECT c.id, c.nombre, c.foto, GROUP_CONCAT(e.nombre SEPARATOR ", ") as especialidades
        FROM colaboradoras c
        LEFT JOIN colaboradora_especialidad ce ON c.id = ce.colaboradora_id
        LEFT JOIN especialidades e ON ce.especialidad_id = e.id
        GROUP BY c.id
    ''')
    colaboradoras = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('colaboradoras.html', especialidades=especialidades, colaboradoras=colaboradoras)

@app.route('/colaboradoras/registrar', methods=['POST'])
def registrar_colaboradora():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion = request.form['direccion']

        foto_file = request.files['foto']
        foto_filename = ''
        if foto_file:
            foto_filename = secure_filename(foto_file.filename)
            foto_path = os.path.join('static/img/colaboradoras', foto_filename)
            foto_file.save(foto_path)

        cursor.execute('''
            INSERT INTO colaboradoras (nombre, telefono, correo, direccion, foto)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, telefono, correo, direccion, foto_filename))
        colaboradora_id = cursor.lastrowid

        especialidades = request.form.getlist('especialidades')
        for esp_id in especialidades:
            cursor.execute('''
                INSERT INTO colaboradora_especialidad (colaboradora_id, especialidad_id)
                VALUES (%s, %s)
            ''', (colaboradora_id, esp_id))

        conn.commit()
        return {"success": True}
    except Exception as e:
        print(e)
        return {"success": False}
    finally:
        cursor.close()
        conn.close()

# Obtener colaboradoras según especialidad
@app.route('/api/colaboradoras/<int:especialidad_id>')
def api_colaboradoras_por_especialidad(especialidad_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.id, c.nombre 
        FROM colaboradoras c
        JOIN colaboradora_especialidad ce ON c.id = ce.colaboradora_id
        WHERE ce.especialidad_id = %s
    ''', (especialidad_id,))
    colaboradoras = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(colaboradoras)

# Obtener horarios disponibles para una colaboradora y fecha (sin tabla agenda_colaboradora)
@app.route('/api/disponibilidad/<int:colaboradora_id>/<fecha>')
def api_disponibilidad(colaboradora_id, fecha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Definir rango horario, ej: de 9 a 18 horas, cada hora
    hora_inicio = 9
    hora_fin = 18

    # Generar lista de horas (formato HH:MM)
    horas_posibles = []
    for h in range(hora_inicio, hora_fin):
        horas_posibles.append(f"{h:02d}:00")

    # Consultar horas ya reservadas para esa colaboradora y fecha
    cursor.execute('''
        SELECT hora FROM reservas
        WHERE fecha = %s AND colaboradora_id = %s
    ''', (fecha, colaboradora_id))
    reservadas = cursor.fetchall()
    horas_reservadas = set(str(r['hora'])[:5] for r in reservadas)

    # Filtrar horas disponibles
    horas_disponibles = [h for h in horas_posibles if h not in horas_reservadas]

    cursor.close()
    conn.close()
    return jsonify(horas_disponibles)

# Modificar /reservar para procesar datos completos
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if 'usuario' not in session or session.get('rol') != 'cliente':
        flash('Debes iniciar sesión para agendar una cita.')
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cliente_id = None
        # Obtener cliente_id desde usuario logueado
        cursor.execute('SELECT id FROM clientes WHERE usuario_id = %s', (session['usuario'],))
        cliente = cursor.fetchone()
        if cliente:
            cliente_id = cliente['id']
        else:
            flash("No se encontró el perfil de cliente.")
            return redirect(url_for('reservar'))

        especialidad_id = request.form.get('especialidad')
        colaboradora_id = request.form.get('colaboradora')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')

        # Validar que recibimos todos los datos
        if not all([especialidad_id, colaboradora_id, fecha, hora]):
            flash("Por favor, completa todos los campos.")
            return redirect(url_for('reservar'))

        # Obtener nombre de especialidad para guardarlo en reservas.servicio
        cursor.execute('SELECT nombre FROM especialidades WHERE id = %s', (especialidad_id,))
        esp = cursor.fetchone()
        if esp is None:
            flash("Especialidad inválida.")
            return redirect(url_for('reservar'))
        servicio_nombre = esp['nombre']

        # Insertar reserva con servicio como texto
        cursor.execute('''
            INSERT INTO reservas (cliente_id, fecha, hora, servicio, colaboradora_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (cliente_id, fecha, hora, servicio_nombre, colaboradora_id))
        conn.commit()
        flash("Reserva realizada con éxito")
        cursor.close()
        conn.close()
        return redirect(url_for('cliente_dashboard'))

    # GET: mostrar formulario
    cursor.execute('SELECT * FROM especialidades')
    especialidades = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('reservar.html', especialidades=especialidades)

if __name__ == '__main__':
    app.run(debug=True)
