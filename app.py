from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import re
from flask_mail import Mail, Message
from trycourier import Courier


app = Flask(__name__)
app.secret_key = "abcd"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'feedbackdb'

mysql = MySQL(app)


client = Courier(auth_token="pk_prod_5CHPPPPC914Q8GP1AGB11EYHCC26")


@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        mail = request.form['email']
        feed = request.form['feedback']
        satisfy = request.form['satisfaction']
        feedback_type = request.form['feedback-type']
        service_name = request.form['service_name']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO feedback (name, phone, email, `feed-back`, satisfaction, product, sp_name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (name, phone, mail, feed, satisfy, feedback_type, service_name))

        mysql.connection.commit()
        cursor.close()
        send_feedback_email(mail)
        return render_template('thank_you.html')

    return render_template('feedback.html')

def send_feedback_email(recipient_email):
    resp = client.send_message(
        message={
          "to": {
            "email": recipient_email
          },
          "content": {
            "title": "Feedback Response",
            "body": "Thank you for your feedback {{joke}}."
          },
          "data":{
            "joke": "Your feedback has been received."
          }
        }
      )      

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (email, password) VALUES (%s, %s)",
                       (email, password))
        mysql.connection.commit()
        cursor.close()
        # After successful signup, redirect to the feedback page
        return render_template('feedback.html')
   
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Check if the email and password are 'admin'
    if email == 'admin@admin.com' and password == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM feedback")  # Assuming 'feedback' is your table name
        user_details = cursor.fetchall()
        cursor.close()

        return render_template('dashboard.html', user_details=user_details)
    else:
        # If the email or password is incorrect, redirect to a login error page
        flash('Invalid email or password', 'error')
        return redirect(url_for('login_error'))

@app.route('/filter', methods=['POST'])
def filter_results():
    category = request.form['category']

    cursor = mysql.connection.cursor()

    # Modify the SQL query based on the selected category
    if category == 'product':
        cursor.execute("SELECT * FROM feedback WHERE product = 'Product'")
    elif category == 'services':
        cursor.execute("SELECT * FROM feedback WHERE product = 'Services'")
    else:
        cursor.execute("SELECT * FROM feedback")

    filtered_results = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', user_details=filtered_results)

if __name__ == '__main__':
    app.run(debug=True)