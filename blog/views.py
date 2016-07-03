from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from .database import User

from . import app
from .database import session, Entry

PAGINATE_BY = 10

@app.route('/')
@app.route('/page/<int:page>')
def entries(page = 1):
    # zero-indexed page
    
    
    limit = None
    try:
        limit = int(request.args.get('limit'))
        if (limit > 0) and (limit < 99999999):
            limit = limit
        else:
            limit = None
    except:
        limit = None
    
    # Python ternary pattern is a bit different than C, JS, and PHP!
    paginate_by = limit if limit else PAGINATE_BY

    page_index = page - 1
    
    count = session.query(Entry).count()
    
    start = page_index * paginate_by
    end = start + paginate_by
    
    # PAGINATE_BY + 1
    total_pages = (count - 1)
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0
    
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    
    return render_template('entries.html', 
        entries = entries,
        has_next = has_next,
        has_prev = has_prev,
        page = page,
        total_pages = total_pages
    )

@app.route('/entry/add', methods=['GET'])
@login_required
def add_entry_get():
    return render_template('add_entry.html')
    
@app.route('/entry/add', methods=['POST'])
@login_required
def add_entry_post():
    entry = Entry(
        title = request.form['title'],
        content = request.form['content'],
        author = current_user,
    )
    session.add(entry)
    session.commit()
    return redirect(url_for('entries'))
    
@app.route('/entry/<int:id>')
def show_entry(id):
    
    entries = session.query(Entry).filter(Entry.id == id)
    return render_template('entries.html',
        entries = entries
    )
    
@app.route('/entry/<int:id>/edit', methods=['GET'])
@login_required
def edit_entry(id):
    
    entry = session.query(Entry).get(id)
    if not entry.author == current_user:
        return 'You are not authorized to edit this record.'
    else:
         return render_template('entry-edit.html',
            entry = entry
        )

@app.route('/entry/<int:id>/edit', methods=['POST'])
@login_required
def save_entry(id):
    
    entry = session.query(Entry).get(id)
    if not entry.author == current_user:
       return 'You are not authorized to edit this record.'
    else:
        print(entry.title)
        entry.title = request.form['title']
        print(entry.title)
        entry.content = request.form['content']
        
        session.commit()
        return redirect(url_for('entries'))
    
@app.route('/entry/<int:id>/delete', methods=['GET'])
@login_required
def confirm_delete_entry(id):
    
    entry = session.query(Entry).get(id)
    if not entry.author.id == current_user.id:
        return 'You are not authorized to delete this record.'
    else:
       return render_template('delete-confirmation.html',
            entry = entry
        )
    
@app.route('/entry/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    
    entry = session.query(Entry).get(id)
    if entry.author == current_user:
        return 'You are not authorized to delete this record.'
    else:
        session.delete(entry)
        return redirect(url_for('entries'))
    
@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')
    
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = session.query(User).filter_by(email = email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Incorrect username or password', 'danger')
        return redirect(url_for('login_get'))
        
    login_user(user)
    return redirect(request.args.get('next') or url_for('entries'))

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    
    return redirect(url_for('entries'))
    
    