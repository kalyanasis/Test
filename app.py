from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = "Secret Key"

#SqlAlchemy Database Configuration With SqLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Employee(db.Model):
    id              = db.Column(db.Integer, primary_key = True)
    first_name      = db.Column(db.String(100))
    last_name       = db.Column(db.String(100))
    email           = db.Column(db.String(100))
    password        = db.Column(db.String(100))
    phone           = db.Column(db.String(100))
    user_type       = db.Column(db.Integer)
    def __init__(self, first_name, last_name,email, password,user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.user_type = user_type

class ProjectList(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    project_name    = db.Column(db.String(200), nullable=False)
    project_description   = db.Column(db.String(200), nullable=True)
    created_by      = db.Column(db.Integer,nullable=False)
    def __init__(self, project_name,project_description,created_by):
        self.project_name = project_name
        self.project_description = project_description
        self.created_by = created_by

    def __repr__(self) -> str:
        return f"{self.id} - {self.project_name}"

class TaskList(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    assign_to   = db.Column(db.Integer,db.ForeignKey('employee.id'),nullable=False)
    created_by  = db.Column(db.Integer,nullable=False)
    project_id  = db.Column(db.Integer,db.ForeignKey('project_list.id'),nullable=False)
    task_title  = db.Column(db.String(200), nullable=True)
    task_description = db.Column(db.String(255), nullable=True)
    created_on  = db.Column(db.String(200), nullable=True)
    taken_on    = db.Column(db.String(200), nullable=True)
    task_status = db.Column(db.String(200), nullable=True)
    remarks     = db.Column(db.String(200), nullable=True)
    def __init__(self, assign_to,created_by,project_id,task_title,task_description,created_on,taken_on,task_status,remarks):
        self.assign_to      = assign_to
        self.created_by     = created_by
        self.project_id     = project_id
        self.task_title     = task_title
        self.task_description = task_description
        self.created_on     = created_on
        self.taken_on       = taken_on
        self.task_status    = task_status
        self.remarks        = remarks

    def __repr__(self) -> str:
        return f"{self.id} - {self.assign_to} - {self.created_by} - {self.project_id}- {self.task_title}- {self.task_description}- {self.created_on}- {self.taken_on}- {self.task_status}- {self.remarks}"


#  New code Start


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            username = getname(request.form['username'])
            return render_template('index.html', data=getfollowedby(username))
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        useremail = request.form['useremail']
        passw = request.form['password']
        print("useremail+++++++++", useremail)
        print("passw+++++++++", passw)

        # try:
        data = Employee.query.filter_by(email=useremail, password=passw).first()
    
        if data is not None:
            session['logged_in'] = True
            session['user_id'] = data.id
            session['user_type'] = data.user_type
            if data.user_type == 0:
                print("session===", session)
                all_data = Employee.query.all()
                all_projects = ProjectList.query.filter_by(created_by = data.id)
                # list_data = TaskList.query.filter_by(created_by=session['user_id']).all()
                list_data = db.session.query(TaskList, Employee).join(Employee)
                return render_template("dashboard.html", employees = all_data,projects = all_projects,task_data = list_data)
            else:                    
                # list_data = TaskList.query.filter_by(assign_to=data.id).all()
                list_data = db.session.query(TaskList, ProjectList).join(ProjectList)
                return render_template('userdashboard.html',task_list = list_data)

            return redirect(url_for('home'))
        else:
            print("else")
            return 'Dont Login'
        # except:
        #     print("error")
        #     return "Dont Login"


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            password=request.form['password'],
            user_email=request.form['user_email'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            user_type=request.form['user_type'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))

#  New Code End


#This is the index route where we are going to
#query on all our employee data
@app.route('/dashboard')
def Index():
    all_data = Employee.query.all()
    if session['user_type'] == 0:
        all_projects    = ProjectList.query.filter_by(created_by = session['user_id'])
        # list_data       = TaskList.query.filter_by(created_by=session['user_id']).all()
        list_data = db.session.query(TaskList, Employee).join(Employee)
        return render_template("dashboard.html", employees = all_data,projects = all_projects,task_data = list_data)
    else:
        # list_data = TaskList.query.filter_by(assign_to=session['user_id']).all()
        list_data = db.session.query(TaskList, ProjectList).join(ProjectList)
        return render_template('userdashboard.html',task_list = list_data)

#this route is for inserting data to SqLite database via html forms
@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == 'POST':
        first_name    = request.form['first_name']
        last_name    = request.form['last_name']
        email   = request.form['email']
        password   = request.form['password']
        user_type = 1
        my_data = Employee(first_name,last_name, email, password,user_type)
        db.session.add(my_data)
        db.session.commit()
        flash("Employee Inserted Successfully")
        return redirect(url_for('Index'))

@app.route('/insertproject', methods = ['POST'])
def insertproject():
    if request.method == 'POST':
        project_name            = request.form['project_name']
        project_description     = request.form['project_description']
        created_by              = session['user_id']
        my_data                 = ProjectList(project_name,project_description,created_by)
        db.session.add(my_data)
        db.session.commit()
        flash("Project Inserted Successfully")
        return redirect(url_for('Index'))

@app.route('/createtask', methods = ['POST'])
def createtask():
    if request.method == 'POST':
        task_title          = request.form['task_title']
        task_description    = request.form['task_description']
        created_by          = session['user_id']
        assign_to           = request.form['assign_to']
        project_id          = request.form['project_id']
        created_on          = datetime.now()
        taken_on            = ""
        task_status         = "To Do"
        remarks             = ""
        my_data             = TaskList(assign_to,created_by,project_id,task_title,task_description,created_on,taken_on,task_status,remarks)
        db.session.add(my_data)
        db.session.commit()
        flash("Task Created Successfully")
        return redirect(url_for('Index'))



#this is our update route where we are going to update our employee
@app.route('/update', methods = ['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data             = Employee.query.get(request.form.get('id'))
        my_data.first_name  = request.form['first_name']
        my_data.last_name   = request.form['last_name']
        my_data.email       = request.form['email']
        my_data.password    = request.form['password']
        db.session.commit()
        flash("Employee Updated Successfully")
        return redirect(url_for('Index'))

@app.route('/projectupdate', methods = ['GET', 'POST'])
def projectupdate():
    if request.method == 'POST':
        my_data = ProjectList.query.get(request.form.get('id'))
        my_data.project_name = request.form['project_name']
        my_data.project_description = request.form['project_description']
        db.session.commit()
        flash("Project Updated Successfully")
        return redirect(url_for('Index'))

@app.route('/updatestatus', methods = ['GET', 'POST'])
def updatestatus():
    if request.method == 'POST':
        my_data = TaskList.query.get(request.form.get('id'))
        task_status = request.form.get('task_status')
        taken_on = my_data.taken_on
        if task_status == "In Progress":
            taken_on = datetime.now()
        my_data.task_status = task_status
        my_data.taken_on = taken_on
        db.session.commit()
        flash("Task Updated Successfully")
        return redirect(url_for('Index'))
        
@app.route('/updatetask', methods = ['GET', 'POST'])
def updatetask():
    if request.method == 'POST':
        my_data = TaskList.query.get(request.form.get('id'))
        task_status = request.form.get('task_status')
        task_title = request.form.get('task_title')
        task_description = request.form.get('task_description')
        project_id = request.form.get('project_id')
        assign_to = request.form.get('assign_to')

        my_data.task_status = task_status
        my_data.task_title = task_title
        my_data.task_description = task_description
        my_data.project_id = project_id
        my_data.assign_to = assign_to


        db.session.commit()
        flash("Task Updated Successfully")
        return redirect(url_for('Index'))



#This route is for deleting our employee
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Employee.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Employee Deleted Successfully")
    return redirect(url_for('Index'))

@app.route('/deletetask/<id>/', methods = ['GET', 'POST'])
def deletetask(id):
    my_data = TaskList.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Task Deleted Successfully")
    return redirect(url_for('Index'))



@app.route('/projectdelete/<id>/', methods = ['GET', 'POST'])
def projectdelete(id):
    my_data = ProjectList.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Project Deleted Successfully")
    return redirect(url_for('Index'))




if __name__ == "__main__":
    app.run(debug=True, port=8000)