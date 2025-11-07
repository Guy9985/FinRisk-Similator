from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import sqlite3
import os
import csv
import io
import math
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change en prod !

# Config DB
Base = declarative_base()
engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    calculations = relationship('Calculation', backref='user')

class Calculation(Base):
    __tablename__ = 'calculations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    gender = Column(String)
    age = Column(Integer)
    calc_type = Column(String)
    interest = Column(String)
    result = Column(String)
    model = Column(String)
    term = Column(Integer, nullable=True)  # Nullable for non-term calculations

# Tables de mortalité
ssa_male_qx = [0.006064, 0.000491, 0.000309, 0.000248, 0.000199, 0.000167, 0.000143, 0.000126, 0.000121, 0.000121, 0.000127, 0.000143, 0.000171, 0.000227, 0.000320, 0.000451, 0.000622, 0.000826, 0.001026, 0.001182, 0.001301, 0.001404, 0.001498, 0.001586, 0.001679, 0.001776, 0.001881, 0.001985, 0.002095, 0.002219, 0.002332, 0.002445, 0.002562, 0.002653, 0.002716, 0.002791, 0.002894, 0.002994, 0.003091, 0.003217, 0.003353, 0.003499, 0.003642, 0.003811, 0.003996, 0.004175, 0.004388, 0.004666, 0.004973, 0.005305, 0.005666, 0.006069, 0.006539, 0.007073, 0.007675, 0.008348, 0.009051, 0.009822, 0.010669, 0.011548, 0.012458, 0.013403, 0.014450, 0.015571, 0.016737, 0.017897, 0.019017, 0.020213, 0.021569, 0.023088, 0.024828, 0.026705, 0.028761, 0.031116, 0.033861, 0.037088, 0.041126, 0.045241, 0.049793, 0.054768, 0.060660, 0.067027, 0.073999, 0.081737, 0.090458, 0.100525, 0.111793, 0.124494, 0.138398, 0.153207, 0.169704, 0.187963, 0.208395, 0.230808, 0.253914, 0.277402, 0.300882, 0.324326, 0.347332, 0.369430, 0.391927]
ssa_female_qx = [0.005119, 0.000398, 0.000240, 0.000198, 0.000160, 0.000134, 0.000118, 0.000109, 0.000106, 0.000106, 0.000111, 0.000121, 0.000140, 0.000162, 0.000188, 0.000224, 0.000276, 0.000337, 0.000395, 0.000450, 0.000496, 0.000532, 0.000567, 0.000610, 0.000650, 0.000699, 0.000743, 0.000796, 0.000855, 0.000924, 0.000988, 0.001053, 0.001123, 0.001198, 0.001263, 0.001324, 0.001403, 0.001493, 0.001596, 0.001700, 0.001803, 0.001905, 0.002009, 0.002116, 0.002223, 0.002352, 0.002516, 0.002712, 0.002936, 0.003177, 0.003407, 0.003642, 0.003917, 0.004238, 0.004619, 0.005040, 0.005493, 0.005987, 0.006509, 0.007067, 0.007658, 0.008305, 0.008991, 0.009681, 0.010343, 0.011018, 0.011743, 0.012532, 0.013512, 0.014684, 0.016025, 0.017468, 0.019195, 0.021195, 0.023452, 0.025980, 0.029153, 0.032394, 0.035888, 0.039676, 0.044156, 0.049087, 0.054635, 0.061066, 0.068431, 0.076841, 0.086205, 0.096851, 0.109019, 0.121867, 0.135805, 0.151108, 0.168020, 0.186340, 0.206432, 0.228086, 0.250406, 0.273699, 0.296984, 0.319502, 0.342716]

cia_male_qx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0003, 0.00032, 0.00035, 0.00037, 0.00038, 0.00038, 0.00038, 0.00037, 0.00037, 0.00036, 0.00035, 0.00035, 0.00035, 0.00034, 0.00034, 0.00033, 0.00032, 0.00032, 0.00031, 0.00031, 0.00031, 0.00031, 0.00032, 0.00032, 0.00034, 0.00035, 0.00037, 0.0004, 0.00042, 0.00045, 0.00048, 0.00051, 0.00054, 0.00057, 0.0006, 0.00064, 0.00068, 0.00073, 0.00079, 0.00087, 0.00095, 0.00106, 0.00119, 0.00134, 0.00152, 0.00172, 0.00196, 0.00222, 0.00251, 0.00283, 0.00318, 0.00356, 0.00396, 0.00439, 0.00485, 0.00534, 0.00584, 0.00638, 0.00694, 0.00752, 0.00812, 0.00875, 0.0094, 0.01007, 0.01076, 0.04572, 0.038639, 0.045045, 0.052775, 0.061889, 0.072465, 0.084822, 0.09933, 0.116433, 0.13567, 0.153743, 0.170609, 0.18893, 0.208156, 0.229128, 0.25146, 0.274498, 0.298597, 0.323061, 0.347696, 0.372492]

cia_female_qx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.000149, 0.000142, 0.000143, 0.000142, 0.000145, 0.000145, 0.000144, 0.00014, 0.000142, 0.000139, 0.000138, 0.000138, 0.00014, 0.000139, 0.000142, 0.00014, 0.000138, 0.00014, 0.00014, 0.000144, 0.000147, 0.00015, 0.00016, 0.000165, 0.00018, 0.000188, 0.000201, 0.000221, 0.000233, 0.00025, 0.00027, 0.000292, 0.000314, 0.000337, 0.000359, 0.000385, 0.000408, 0.000437, 0.000473, 0.000524, 0.000574, 0.000643, 0.000725, 0.000818, 0.00093, 0.001057, 0.001214, 0.001381, 0.001561, 0.001749, 0.001958, 0.002198, 0.002455, 0.00275, 0.003085, 0.003447, 0.00382, 0.004258, 0.004727, 0.005208, 0.005688, 0.006203, 0.006731, 0.007258, 0.007795, 0.033281, 0.038639, 0.045045, 0.052775, 0.061889, 0.072465, 0.084822, 0.09933, 0.116433, 0.13567, 0.153743, 0.170609, 0.18893, 0.208156, 0.229128, 0.25146, 0.274498, 0.298597, 0.323061, 0.347696, 0.372492]

# Updated cima_male_qx with extracted values (CIMA H)
cima_male_qx = [
0.005368, 0.00073, 0.000559, 0.000476, 0.000407, 0.000371, 0.000334, 0.000316, 0.000316, 0.000297, 0.000316, 0.000316, 0.000372, 0.000442, 0.000543, 0.000716, 0.000907, 0.001128, 0.001337, 0.001489, 0.001578, 0.001633, 0.001665, 0.001689, 0.001721, 0.001753, 0.0018, 0.001847, 0.001895, 0.001948, 0.001993, 0.002037, 0.002108, 0.002205, 0.002342, 0.002477, 0.002638, 0.002809, 0.003004, 0.003233, 0.003497, 0.003816, 0.004143, 0.004501, 0.004877, 0.005271, 0.005663, 0.006041, 0.006408, 0.006774, 0.007141, 0.00754, 0.007962, 0.008406, 0.008884, 0.009375, 0.009885, 0.010595, 0.011416, 0.012457, 0.013526, 0.014816, 0.016146, 0.017517, 0.019128, 0.020784, 0.02254, 0.024163, 0.025912, 0.027789, 0.02982, 0.032014, 0.034342, 0.036827, 0.039498, 0.042415, 0.045624, 0.049122, 0.057439, 0.062563, 0.068398, 0.074844, 0.08175, 0.088986, 0.096665, 0.104879, 0.113595, 0.122792, 0.132356, 0.142255, 0.160604, 0.191187, 0.226765, 0.267793, 0.314613, 0.367363, 0.425885, 0.489604, 0.557429, 0.627667, 0.698026, 0.765727, 0.827772, 0.88138, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
]

# CIMA F not found; keep approximation or update similarly
cima_female_qx = [0.070, 0.060, 0.050, 0.040, 0.030, 0.025, 0.020, 0.015, 0.012, 0.010, 0.008, 0.007, 0.006, 0.005, 0.004, 0.003, 0.003, 0.003, 0.003, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.010, 0.012, 0.014, 0.016, 0.018, 0.020, 0.023, 0.026, 0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060, 0.065, 0.070, 0.075, 0.080, 0.085, 0.090, 0.095, 0.100, 0.105, 0.110, 0.115, 0.120, 0.125, 0.130, 0.135, 0.140, 0.145, 0.150, 0.155, 0.160, 0.165, 0.170, 0.175, 0.180, 0.185, 0.190, 0.195, 0.200, 0.205, 0.210, 0.215, 0.220, 0.225, 0.230, 0.235, 0.240, 0.245, 0.250, 0.255, 0.260, 0.265, 0.270, 0.275, 0.280, 0.285, 0.290, 0.295, 0.300, 0.305, 0.310, 0.315, 0.320, 0.325, 0.330, 0.335, 0.340, 0.345, 0.350, 0.355, 0.360]

qx_dicts = {
    'ssa': {'male': ssa_male_qx, 'female': ssa_female_qx},
    'cia': {'male': cia_male_qx, 'female': cia_female_qx},
    'cima': {'male': cima_male_qx, 'female': cima_female_qx}
}

max_age = 100

def get_qx(gender, model):
    if 'custom_qx' in session and gender in session['custom_qx']:
        return session['custom_qx'][gender]
    if model in qx_dicts:
        return qx_dicts[model][gender]
    return []

def get_qx_at_age(age, gender, model, params=None):
    if model == 'gompertz':
        if params is None:
            params = {'a': 0.00005, 'b': 0.1}
        mu = params['a'] * math.exp(params['b'] * age)
        return 1 - math.exp(-mu)
    else:
        qx = get_qx(gender, model)
        if age >= len(qx):
            return 1.0
        return qx[age]

def calculate_life_expectancy(age, gender, model='ssa', params=None):
    if age > max_age:
        return 0
    e = 0.0
    p = 1.0
    for k in range(1, max_age - age + 1):
        q = get_qx_at_age(age + k - 1, gender, model, params)
        p *= (1 - q)
        e += p
    return e + 0.5

def calculate_annuity(age, gender, interest_rate, model='ssa', params=None):
    if age > max_age:
        return 0
    i = interest_rate / 100.0
    v = 1 / (1 + i)
    a = 0.0
    p = 1.0
    vk = 1.0
    a += vk * p
    for k in range(1, max_age - age + 1):
        q = get_qx_at_age(age + k - 1, gender, model, params)
        vk *= v
        p *= (1 - q)
        a += vk * p
    return a

def calculate_life_insurance(age, gender, interest_rate, model='ssa', params=None):
    if age > max_age:
        return 0
    i = interest_rate / 100.0
    v = 1 / (1 + i)
    A = 0.0
    p = 1.0
    vk = v
    for k in range(0, max_age - age):
        q = get_qx_at_age(age + k, gender, model, params)
        A += vk * p * q
        p *= (1 - q)
        vk *= v
    return A

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db_session = Session()
    user = db_session.query(User).get(int(user_id))
    db_session.close()
    return user

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        db_session = Session()
        if db_session.query(User).filter_by(username=username).first():
            db_session.close()
            return 'Utilisateur existe déjà'
        user = User(username=username, password=password)
        db_session.add(user)
        db_session.commit()
        db_session.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_session = Session()
        user = db_session.query(User).filter_by(username=username).first()
        db_session.close()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.json
    gender = data['gender']
    age = int(data['age'])
    calc_type = data['calculation']
    model = data.get('model', 'ssa')
    params = None
    if model == 'gompertz':
        params = {'a': float(data.get('gompertz_a', 0.00005)), 'b': float(data.get('gompertz_b', 0.1))}
    interest = float(data.get('interest', 0))
    term = int(data.get('term', None)) if calc_type in ['endowment', 'term_insurance'] else None

    if calc_type == 'life_expectancy':
        result = calculate_life_expectancy(age, gender, model, params)
    elif calc_type == 'annuity':
        result = calculate_annuity(age, gender, interest, model, params)
    elif calc_type == 'life_insurance':
        result = calculate_life_insurance(age, gender, interest, model, params)
    else:
        return jsonify({'error': 'Type de calcul invalide'}), 400

    db_session = Session()
    calc = Calculation(user_id=current_user.id, gender=gender, age=age, calc_type=calc_type, interest=str(interest) if interest else None, result=str(result), model=model, term=term)
    db_session.add(calc)
    db_session.commit()
    db_session.close()

    return jsonify({'result': round(result, 2)})

@app.route('/history')
@login_required
def history():
    db_session = Session()
    calcs = db_session.query(Calculation).filter_by(user_id=current_user.id).all()
    db_session.close()
    return render_template('history.html', calcs=calcs)

@app.route('/upload_custom', methods=['POST'])
@login_required
def upload_custom():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        reader = csv.reader(io.StringIO(file.read().decode('utf-8')))
        male_qx = []
        female_qx = []
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 3:
                male_qx.append(float(row[1]))
                female_qx.append(float(row[2]))
        session['custom_qx'] = {'male': male_qx[:101], 'female': female_qx[:101]}
        return 'Table uploadée !'
    return 'Erreur upload'

@app.route('/generate_pdf')
@login_required
def generate_pdf():
    model = request.args.get('model', 'ssa')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Table de Mortalité Complète", ln=1, align='C')
    pdf.cell(40, 10, 'Âge', 1)
    pdf.cell(50, 10, 'qx Male', 1)
    pdf.cell(50, 10, 'qx Female', 1)
    pdf.cell(30, 10, 'lx Male', 1)
    pdf.cell(30, 10, 'lx Female', 1)
    pdf.ln()
    lx_male = 100000
    lx_female = 100000
    for age in range(0, max_age + 1):
        qx_m = get_qx('male', model)[age] if age < len(get_qx('male', model)) else 1.0
        qx_f = get_qx('female', model)[age] if age < len(get_qx('female', model)) else 1.0
        pdf.cell(40, 10, str(age), 1)
        pdf.cell(50, 10, f"{qx_m:.6f}", 1)
        pdf.cell(50, 10, f"{qx_f:.6f}", 1)
        pdf.cell(30, 10, str(round(lx_male)), 1)
        pdf.cell(30, 10, str(round(lx_female)), 1)
        pdf.ln()
        lx_male *= (1 - qx_m)
        lx_female *= (1 - qx_f)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name='table_mortalite.pdf', mimetype='application/pdf')

@app.route('/export_result/<int:calc_id>')
@login_required
def export_result(calc_id):
    db_session = Session()
    calc = db_session.query(Calculation).get(calc_id)
    db_session.close()
    if calc and calc.user_id == current_user.id:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Résultat Calcul: {calc.calc_type}", ln=1)
        pdf.cell(200, 10, txt=f"Genre: {calc.gender}, Âge: {calc.age}, Résultat: {calc.result}", ln=1)
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return send_file(pdf_output, as_attachment=True, download_name='resultat.pdf', mimetype='application/pdf')
    return 'Non autorisé'

if __name__ == '__main__':
    # Recreate database to add new columns
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app.run(debug=True)