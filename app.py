from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia por una clave secreta real

# Configuración de la base de datos MySQL (Asegúrate de que los valores sean correctos)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/estetica'  # Cambia 'root' y 'password' por tus credenciales
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='administrador')

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_servicio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(255), nullable=True)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_telefonico = db.Column(db.String(15), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    apellido_cliente = db.Column(db.String(100), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id'), nullable=False)
    servicio = db.relationship('Servicio', backref=db.backref('citas', lazy=True))

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            session['usuario_id'] = usuario.id
            return redirect(url_for('dashboard'))
        else:
            return 'Usuario o contraseña incorrectos'
    
    return render_template('login.html')

# Ruta para el dashboard del administrador
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    servicios = Servicio.query.all()
    return render_template('dashboard.html', servicios=servicios)

# Ruta para agendar citas
@app.route('/agendar_cita', methods=['GET', 'POST'])
def agendar_cita():
    if request.method == 'POST':
        numero_telefonico = request.form['numero_telefonico']
        fecha = request.form['fecha']
        nombre_cliente = request.form['nombre_cliente']
        apellido_cliente = request.form['apellido_cliente']
        servicio_id = request.form['servicio_id']
        
        cita = Cita(
            numero_telefonico=numero_telefonico,
            fecha=fecha,
            nombre_cliente=nombre_cliente,
            apellido_cliente=apellido_cliente,
            servicio_id=servicio_id
        )
        db.session.add(cita)
        db.session.commit()
        
        return redirect(url_for('citas'))
    
    servicios = Servicio.query.all()
    return render_template('agendar_cita.html', servicios=servicios)

# Ruta para mostrar todas las citas
@app.route('/citas')
def citas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    citas = Cita.query.all()
    return render_template('citas.html', citas=citas)

# Inicializar la base de datos (crear tablas si no existen)
@app.before_first_request
def init_db():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
