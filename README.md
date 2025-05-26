# Flask Authentication System using OTP

A secure Flask web application implementing user registration with email OTP verification, login, password reset, and forgot password functionalities using MySQL as the database backend. Passwords and OTPs are hashed with Bcrypt, and CSRF protection is enabled for all forms.

## Features

- User registration with OTP email verification (Gmail-only addresses).
- User login with hashed password validation.
- Password reset via OTP email verification.
- Forgot password flow with OTP verification.
- Account deletion and logout functionality.
- Session management with 15-minute timeout.
- Secure password policies enforced (uppercase, lowercase, special character, length).
- Email sending using Flask-Mail with SMTP (Gmail).

## Prerequisites

- Python 3.x
- MySQL server installed and running
- A Gmail account with app password for SMTP (2FA enabled recommended)

## Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the MySQL database:**

- The program automatically creates the database and necessary tables. Just fill in the password.
  
  ```python
  mydb=con.connect(host='localhost',user='root',password='<your-sql-password>')
  ```

5. **Update the application configuration:**

- Edit the `app.py` file to set your MySQL and email credentials:

    ```python
    app.config['MAIL_USERNAME']="your-email@gmail.com"
    app.config['MAIL_PASSWORD']="your-email-app-password"
    ```

- **Note:** Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail SMTP if 2FA is enabled.

## Running the Application

1. **Start the Flask development server:**

    ```bash
    python app.py
    ```

2. **Access the application:**

    Open your web browser and navigate to `http://127.0.0.1:5000/`.


## Application Flow

### Registration

- Register using a Gmail address only.
- The app sends a 6-character OTP to your email.
- Verify the OTP to proceed to password creation with password validation:
  - Minimum 6 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one special character
  - Password confirmation must match

### Login

- Enter your email and password to log in.
- On success, redirected to the dashboard.

### Dashboard

- After login, access dashboard.
- Options to logout or delete your account.

### Forgot Password

- Submit your registered Gmail to receive an OTP.
- Verify OTP and set a new password following the password rules.

---

## Password Validation Rules

- At least 6 characters
- Must contain uppercase and lowercase letters
- Must include at least one special character (`!@#$%^&*(),.?":{}|<>`)
- Password and confirmation must match

---

## Dependencies

- Flask
- Flask-Bcrypt
- Flask-WTF (for CSRF protection)
- Flask-Mail
- mysql-connector-python

---

## Security Notes

- Passwords and OTPs are hashed securely with Bcrypt.
- CSRF protection enabled on all forms.
- Session lifetime is 15 minutes.
- Email verification and OTPs are sent securely over SMTP.

---
