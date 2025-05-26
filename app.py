# Libraries ======================================================================================================

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
import mysql.connector as con
import re
from datetime import timedelta
import random
import string

# Pre Setup ======================================================================================================

mydb=con.connect(host='localhost',user='root',password='nehal292004!')
mycur = mydb.cursor()

query = "show databases"
mycur.execute(query)
existing_database = [db[0] for db in mycur.fetchall()]
if "flask_login" not in existing_database:
    query = "create database flask_login"
    mycur.execute(query)
    mycur.close()
    mydb.close()

mydb=con.connect(host='localhost',user='root',password='nehal292004!', db = "flask_login")
mycur = mydb.cursor()
query = "show tables"
mycur.execute(query)
existing_tables = [table[0] for table in mycur.fetchall()]
if "users" not in existing_tables:
    query = "create table users (email varchar(100) not NULL Primary key, password varchar(250) not Null)"
    mycur.execute(query)
if "otps" not in existing_tables:
    query = "create table otps (email varchar(100) not NULL Primary key, otp varchar(250) not Null)"
    mycur.execute(query)
    
# Start Flask ====================================================================================================

app = Flask(__name__)

app.secret_key = 'your_very_secret_key_here'
app.permanent_session_lifetime = timedelta(minutes=15)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'trialandthrow@gmail.com'
app.config['MAIL_PASSWORD'] = 'gbho jqdl yepg srkz'
mail = Mail(app)

bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)

# Validation Functions ===========================================================================================

def validate_password(password, cpassword):
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return "Password must contain at least one special character."
    if password != cpassword:
        return "Passwords do not match."
    return None

# Main ===========================================================================================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "error")
        else:
            query = "SELECT password FROM users WHERE email = %s"
            mycur.execute(query, (email,))
            usersdata = mycur.fetchone()
            
            if usersdata:
                if bcrypt.check_password_hash(usersdata[0], password):
                    session['user'] = email
                    return redirect(url_for('dashboard'))
                else: 
                    flash("Incorrect email or password.", "error")
            else:
                flash("Email does not exist.", "error")

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'delete' in request.form:
            email = session['user']
            query = "DELETE FROM users WHERE email = %s"
            mycur.execute(query, (email,))
            mydb.commit()
            session.clear()
            flash("Account deleted successfully.", "success")
            return redirect(url_for('login'))

        elif 'submit' in request.form:
            session.clear()
            flash("Logged out successfully.", "success")
            return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
    
        query = "SELECT * FROM users WHERE email = %s"
        mycur.execute(query, (email,))
        usersdata = mycur.fetchone()

        if usersdata:
            flash("User already exists.", "error")
        elif not email.endswith('@gmail.com'):
            flash("Only Gmail addresses are allowed.", "error")
        else:
            flash("Verification of email sent", "success")
            
            all_chars = string.ascii_letters + string.digits
            random_string = ''.join(random.choices(all_chars, k=6))
            hashed_rs = bcrypt.generate_password_hash(random_string).decode('utf-8')
            
            query = "INSERT INTO otps (email, otp) VALUES (%s, %s) ON DUPLICATE KEY UPDATE otp = VALUES(otp)"
            mycur.execute(query, (email, hashed_rs, ))
            mydb.commit()
            
            msg = Message("Your OTP Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Your Email verification OTP code is: {random_string}"
            mail.send(msg)
            session['register'] = email
            return render_template('register_otp.html', email=email)
        
    return render_template('register_mail.html')

@app.route('/set_password', methods=['GET', 'POST'])
def register2():
    
    if 'register' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        otp = request.form.get('otp')
        
        query = "SELECT otp FROM otps WHERE email = %s"
        mycur.execute(query, (email,))
        realotp = mycur.fetchone()
        
        error = validate_password(password, cpassword)
        if error:
            flash(error, "error")
            return render_template('register_otp.html', email=email)
        else:
            if bcrypt.check_password_hash(realotp[0], otp):
                hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
                query = "insert into users values(%s, %s)"
                mycur.execute(query, (email, hashed_pw))
                mydb.commit()
                flash("User registration success", "success")
                session.pop("register", None)
                return redirect(url_for('login'))
            else:
                flash("Wrong OTP", "error")
                return render_template('register_otp.html', email=email)

    return render_template('register_otp.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        email = request.form.get('email')

        query = "SELECT * FROM users WHERE email = %s"
        mycur.execute(query, (email,))
        usersdata = mycur.fetchone()

        if usersdata:
            all_chars = string.ascii_letters + string.digits
            random_string = ''.join(random.choices(all_chars, k=6))
            hashed_rs = bcrypt.generate_password_hash(random_string).decode('utf-8')
            
            query = "INSERT INTO otps (email, otp) VALUES (%s, %s) ON DUPLICATE KEY UPDATE otp = VALUES(otp)"
            mycur.execute(query, (email, hashed_rs, ))
            mydb.commit()
            
            msg = Message("Your OTP Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Your Password reset OTP code is: {random_string}"
            mail.send(msg)
            session['resetpassword'] = email
            return render_template('password_otp.html', email = email)
        
        else:
            flash("User does not exists", "error")
            return redirect(url_for('verification'))

    return render_template('password_mail.html')

@app.route('/set_new_password', methods=['GET', 'POST'])
def passwordset():
    
    if 'resetpassword' not in session:
        return redirect(url_for('verification'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        otp = request.form.get('otp')
        
        query = "SELECT otp FROM otps WHERE email = %s"
        mycur.execute(query, (email,))
        realotp = mycur.fetchone()
        
        error = validate_password(password, cpassword)
        if error:
            flash(error, "error")
            return render_template('register_otp.html', email=email)
        else:
            if bcrypt.check_password_hash(realotp[0], otp):
                hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
                query = "update users set password = %s WHERE email = %s"
                mycur.execute(query, (hashed_pw, email,))
                mydb.commit()
                session.pop("resetpassword", None)
                flash("New password updated", "success")
                return redirect(url_for('login'))
            else:
                flash("Wrong OTP", "error")
                return render_template('password_otp.html', email=email)
            
    return render_template('password_otp.html')

# initialize =====================================================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)