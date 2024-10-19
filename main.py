from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///savings.db'
app.config['UPLOAD_FOLDER'] = 'static/'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(150), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    goal_amount = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(150), nullable=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

# Create tables at startup
with app.app_context():
    db.create_all()

# Routes
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists. Choose a different username.", "danger")
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    funds = Fund.query.filter_by(owner_id=current_user.id).all()
    return render_template('dashboard.html', funds=funds)

@app.route('/create_fund', methods=['GET', 'POST'])
@login_required
def create_fund():
    if request.method == 'POST':
        title = request.form['title']
        goal_amount = float(request.form['goal_amount'])
        image = request.files.get('image')
        image_file = None
        if image:
            image_file = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))

        new_fund = Fund(owner_id=current_user.id, title=title, goal_amount=goal_amount, image_file=image_file)
        db.session.add(new_fund)
        db.session.commit()
        flash("Fund created successfully.", "success")
        return redirect(url_for('dashboard'))
    return render_template('create_fund.html')

@app.route('/fund/<public_id>', methods=['GET', 'POST'])
@login_required
def view_fund(public_id):
    fund = Fund.query.filter_by(public_id=public_id).first_or_404()
    if request.method == 'POST':
        if 'total_amount' in request.form:
            total_amount = float(request.form['total_amount'])
            if fund.total_amount < fund.goal_amount:
                fund.total_amount += total_amount
                db.session.commit()
                flash(f"Updated amount for {fund.title}", "success")
            else:
                flash("Goal already reached! You can't add more funds.", "warning")
        elif 'goal_amount' in request.form:
            new_goal_amount = float(request.form['goal_amount'])
            if new_goal_amount > fund.total_amount:
                fund.goal_amount = new_goal_amount
                db.session.commit()
                flash(f"Goal amount updated to {new_goal_amount} for {fund.title}", "success")
            else:
                flash("New goal amount must be greater than the current total amount.", "warning")
    return render_template('fund_view.html', fund=fund)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
