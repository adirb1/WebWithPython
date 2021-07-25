from forms import AddTaskForm
from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for
from flask_sqlalchemy import SQLAlchemy


# config
app = Flask(__name__) # take the name of the current module
app.config.from_object('_config') # configuration stuff
db=SQLAlchemy(app)



# helper functions



def login_required(test): # check that the user is login
    @wraps(test) # extend function capabilities
    def wrap(*args, **kwargs):# when we not sure about the amount of arguments the function will get
        if 'logged_in' in session: # if the user is logged in
            return test(*args, **kwargs) # return information
        else:
            flash('You need to login first.') # if not alert the user that he must log in
            return redirect(url_for('login')) # return him to the login page
    return wrap


# route handlers
@app.route('/logout/') # routing the logout page
def logout():
    session.pop('logged_in', None)  # stop the logged in session and logout the user
    flash('Goodbye!')
    return redirect(url_for('login')) # return the user to the login page

@app.route('/', methods=['GET', 'POST']) # routhe the main page , here we will both ask for data and send data
def login():
    if request.method == 'POST': # in case we want to send data
        if request.form['username'] != app.config['USERNAME'] \
                or request.form['password'] != app.config['PASSWORD']:  # in case the username or password are incorrect return error
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    else:
        session['logged_in'] = True # set the session to login so the user can view his info
        flash('Welcome!')
        return redirect(url_for('tasks')) # take him to his tasks page
    return render_template('login.html')


@app.route('/tasks/')
@login_required
def tasks():
    open_tasks = db.session.query(Task) \
        .filter_by(status='1').order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task) \
        .filter_by(status='0').order_by(Task.due_date.asc())
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks
    )

# Add new tasks
@app.route('/add/', methods=['GET','POST'])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                '1'
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
    return redirect(url_for('tasks'))


# Mark tasks as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
   new_id=task_id
   db.session.query(Task).filter_by(task_id=new_id).update({"status":"0"})
   db.session.commit()
   flash('The task is complete')
   return redirect(url_for('tasks'))


# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash('The task was deleted. Why not add a new one?')
    return redirect(url_for('tasks'))
