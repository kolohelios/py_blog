from flask import render_template, request, redirect, url_for

from . import app
from .database import session, Entry

PAGINATE_BY = 10

@app.route('/')
@app.route('/page/<int:page>')
def entries(page = 1):
    # zero-indexed page
    
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
def add_entry_get():
    return render_template('add_entry.html')
    
@app.route('/entry/add', methods=['POST'])
def add_entry_post():
    entry = Entry(
        title = request.form['title'],
        content = request.form['content'],
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
def edit_entry(id):
    
    entry = session.query(Entry).filter(Entry.id == id)[0]
    return render_template('entry-edit.html',
        entry = entry
    )

@app.route('/entry/<int:id>/edit', methods=['POST'])
def save_entry(id):
    
    entry = session.query(Entry).get(id)
    print(entry.title)
    entry.title = request.form['title']
    print(entry.title)
    entry.content = request.form['content']
    
    session.commit()
    return redirect(url_for('entries'))
    
@app.route('/entry/<int:id>/delete', methods=['GET'])
def confirm_delete_entry(id):
    
    entry = session.query(Entry).get(id)
    
    return render_template('delete-confirmation.html',
        entry = entry
    )
    
@app.route('/entry/<int:id>/delete', methods=['POST'])
def delete_entry(id):
    
    entry = session.query(Entry).get(id)
    
    session.delete(entry)
    return redirect(url_for('entries'))