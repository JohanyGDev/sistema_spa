from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from database import init_db, crear_tabla_usuarios, crear_tabla_admin, insertar_admin_por_defecto

app = Flask(__name__)  # Crear la aplicación Flask
app.secret_key = 'clave_secreta_segura'  # Clave necesaria para manejar sesiones

# Inicializar la base de datos y las tablas necesarias
init_db()                    # Tabla de reservas
crear_tabla_usuarios()       # Tabla de usuarios con roles (admin y cliente)
crear_tabla_admin()          # Opcional si tienes tabla solo para admin (puedes quitarla si unificas)
insertar_admin_por_defecto() # Insertar un admin por defecto si la tabla está vacía

# Ruta de inicio
@app.route('/')
def home():
    return render_template('home.html')

# Página de servicios
@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

# Formulario de reservas (solo para clientes)
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        servicio = request.form['servicio']
        fecha = request.form['fecha']

        # Guardar la reserva en la base de datos
        conn = sqlite3.connect('spa.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reservas (nombre, servicio, fecha)
            VALUES (?, ?, ?)
        ''', (nombre, servicio, fecha))
        conn.commit()
        conn.close()

        return f"<h2>Gracias, {nombre}. Tu cita para '{servicio}' fue agendada para el {fecha}.</h2><a href='/'>Volver al inicio</a>"
    
    return render_template('reservar.html')

# Página de login (inicio de sesión)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = sqlite3.connect('spa.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?', (usuario, contrasena))
        usuario_encontrado = c.fetchone()
        conn.close()

        if usuario_encontrado:
            # Guardar datos en sesión
            session['usuario'] = usuario_encontrado[2]  # campo 'usuario'
            session['rol'] = usuario_encontrado[4]      # campo 'rol': 'admin' o 'cliente'

            if session['rol'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('cliente_dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')

# Panel del administrador (ver reservas)
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

# Panel del cliente (aún por desarrollar)
@app.route('/cliente')
def cliente_dashboard():
    if 'usuario' not in session or session['rol'] != 'cliente':
        return redirect(url_for('login'))
    
    return f"<h2>Bienvenido cliente: {session['usuario']}</h2><a href='/'>Volver al inicio</a>"

# Eliminar una reserva (solo admins)
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

# Cerrar sesión (logout)
@app.route('/logout')
def logout():
    session.clear()  # Elimina todos los datos de sesión
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)  # Iniciar la aplicación en modo desarrollo
