import re
from flask import Flask, session, request, redirect, render_template, flash, url_for

import db.data_layer as db
'''
USAGE:        db.<function_name>
EXAMPLES:     db.search_by_user_or_email('Smith')
              db.search_by_user_or_email('gmail.com')
'''

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

app = Flask(__name__)
app.secret_key = '0d599f0ec05c3bda8c3b8a68c32a1b47'

@app.route('/')
def index():
    db_quotes = db.get_all_quotes()
    return render_template('index.html', quotes = db_quotes)

@app.route('/create_quote', methods=['POST'])
def create_quote():
    user_id = session['user_id']
    content = request.form['html_content']
    db.create_quote(user_id, content)
    return redirect(url_for('index'))

@app.route('/delete/<quote_id>')
def delete_quote(quote_id):
    db.delete_quote(quote_id)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    return redirect(url_for('search_results', query=request.args['html_query']))

@app.route('/results/<query>')
def search_results(query):
    db_quotes = db.search_by_content(query) 
    db_users = db.search_by_user_or_email(query)

    return render_template('search_results.html', quotes = db_quotes, users = db_users)

@app.route('/user/<user_id>/')
def user_quotes(user_id):
    db_quotes = db.get_all_quotes_for(user_id)
    return render_template('index.html', quotes = db_quotes)

@app.route('/register/authenticate')
def register_authenticate():
    return render_template('register_authenticate.html')

@app.route('/login/authenticate')
def login_authenticate():
    return render_template('login_authenticate.html')

def setup_web_session(user):
    pass

@app.route('/register', methods = ['POST'])
def register():
    server_email = request.form['html_email']
    server_username = request.form['html_username']
    server_password = request.form['html_password']
    server_confirm = request.form['html_confirm']

    is_valid = True

    if server_password != server_confirm:
        flash('passwords are not the same')
        is_valid = False

    if is_empty('email', request.form):
        is_valid = False

    if is_empty('username', request.form):
        is_valid = False

    if is_empty('password', request.form):
        is_valid = False

    if not is_valid:
        return redirect(url_for('register_authenticate'))

    user = db.create_user(server_email, server_username, server_password)

    session['user_id'] = user.id
    session['username'] = user.username

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login', methods = ['POST'])
def login():
    try:
        user = db.get_user_by_email(request.form['html_email'])
        if user.password == request.form['html_password']:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
    except:
        pass

    flash('invalid login')
    return redirect(url_for('login_authenticate'))

def is_empty(field_name, form):
    key = 'html_{}'.format(field_name)
    empty = not len(form[key])>0
    if empty:
        flash('{} is empty'.format(field_name))
    
    return empty


app.run(debug=True)