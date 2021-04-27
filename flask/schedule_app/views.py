import psycopg2
import hashlib 
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session, g
from schedule_app import app, mail
from .myform import * 
from .PostgresSQLdb import SQLqueries
from functools import wraps
from datetime import datetime, date, time,timedelta
from copy import deepcopy, copy
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return  redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (session.get('logged_in') and session.get('admin')):
            return  redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('logged_in', None)
    session.pop('username',  None)
    session.pop('surname',   None)
    session.pop('name',      None)
    session.pop('admin',     None)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'] )
def login( ):
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form =   LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = '\\x' + hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
        print(password)
        userDict = db.CheckUser(user, password)
        db.Close()
        if(len(userDict) == 1):
            userDict = userDict[0]
            if(userDict[0] == user):
               if(userDict[1] == password):
                   session['logged_in'] = True
                   session['username']  = user
                   session['surname'] = userDict[2]
                   session['name']    = userDict[3]
                   session['admin']   = userDict[4]
                   return redirect('/')
        else :
            error = 'Пароль або логін невірний! Спробуйте знову.'
            return render_template('login.html', form=form, error=error)

    return  render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form =   RegisterForm()
    if form.validate_on_submit():
        try:
            db = SQLqueries()
        except:
            return render_template('Error404.html')
        username = form.username.data
        surname  = form.surname.data
        name     = form.name.data
        ochestvo = form.ochestvo.data
        password = form.password.data
        email    = form.email.data
        try:
            db.SingUp(username, surname, name, ochestvo, password, email)
        except (Exception, psycopg2.DatabaseError) as error:
            message = str(error)
            return render_template('signup.html', form=form, message=message)
        finally:
            db.Close()

        return redirect('/login')
    
    return render_template('signup.html', form=form)


s = URLSafeTimedSerializer('Thisisasecret!')
@app.route('/ForgotPassword',  methods=['GET', 'POST'])
def ForgotPassword():
   form = MyEmail()
   if form.validate_on_submit():
        try:
            db = SQLqueries()
        except:
            return render_template('Error404.html')
        email = form.email.data
        if db.CheckEmail(email):
            message = "Лист для відновлення пароля відправлино!"
            token =s.dumps(email, salt='email-confirm')
            msg = Message('Hello', sender = 'testboss@ukr.net', recipients = [email])
            Link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Ссилка для відновленя пароля: {}'.format(Link)
            mail.send(msg)
        else:
            message = "I dose not exist"
        db.Close()
        return render_template('ForgotPassword.html', form = form, message =  message)
   return render_template('ForgotPassword.html', form = form)

@app.route('/confirm_email/<token>',  methods=['GET', 'POST'])
def confirm_email(token):
    form = ChangePassword()
    try:
        email = s.loads(token ,salt='email-confirm', max_age=3600)
    except :
         return '<h1>The token is expired!</h1>'
    if form.validate_on_submit():
       password = form.password.data
       try:
            db = SQLqueries()
       except:
            return "Error404"
       try:
           db.ChangePassword(email, password)
       except (Exception) as error:
           db.Close()
           message = "Помилка : " + str(error)
           return render_template('ChangePassword.html', form = form, token=token, message = message)
       db.Close()
       return redirect('/login')
      
    return render_template('ChangePassword.html', form = form, token=token)

def GenerateDate(ds,de):
    start =  datetime.strptime(ds,   '%Y-%m-%d')
    end =    datetime.strptime(de,   '%Y-%m-%d')
    step =   timedelta(days=1)
    rangeDate = []
    while start <= end:
        if not datetime.isoweekday(start.date()) in [6,7]:
            rangeDate.append(start.date())
        start += step
    return rangeDate


def InitDate():
    vToday = datetime.today().date()  
    endDay = vToday + timedelta(days=7)
    rangeDate =  GenerateDate(str(vToday), str(endDay))
    rDic = {'TODAY' : vToday, 'END': endDay, 'R': rangeDate}
    return rDic


@app.route('/', methods=['GET', 'POST'])
@app.route('/info', methods=['GET', 'POST'])
def info():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vGroups = db.GetGroups() 
    if vGroups:
        VG = vGroups[0][0]
    else:
        VG = ""
    form =   DateForm()
    if form.validate_on_submit():
      vFrom = form.dateFrom.data
      vTo   = form.dateTo.data
      select = request.form['Groups']
      if vFrom < vTo: 
        rangeDate  = GenerateDate(str(vFrom), str(vTo))
        dateDic= db.GetLesson(str(vFrom),str(vTo), select)
        db.Close()
        return render_template('info.html', dateDic=dateDic, 
                               rangeDate=rangeDate, vGroups=vGroups, form=form)
      else:
          error = 'Дата начала должна быть меньше даты конца!'
          return render_template('info.html', error=error, vGroups=vGroups ,form=form)
    todayDic = InitDate()
    dateDic= db.GetLesson(todayDic['TODAY'], todayDic['END'], VG)
    db.Close()
    return render_template('info.html', dateDic=dateDic, 
                           rangeDate=todayDic['R'], vGroups=vGroups, form=form)

###Insert
@app.route('/InsertLessons', methods=['GET', 'POST'])
@login_required_admin
def InsertLessons():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form        = ILessonsForm()
    vTeacher    = db.GetAllTeachers()
    vSubjects   = db.GetAllSubjects()
    vGroups     = db.GetGroups()
    vClassrooms = db.GetClassrooms()
    vLessons    = db.GetLesson2()
    message = None
    if form.validate_on_submit():
        vInput = {}
       
        vInput['teacher']    = form.teacher.data
        vInput['subject']    = form.subject.data
        vInput['dateFrom']   = form.dateFrom.data
        vInput['dateTo']     = form.dateTo.data
        vInput['groups']     = form.groups.data
        
        vInput['building']   = form.classroom.data.split('-')[0]
        vInput['classroom']  = form.classroom.data.split('-')[1]
        vInput['para']       = request.form['para']
        vInput['f']          = request.form['f']
        vInput['typelesson'] = request.form['typelesson']
        try:
            db.AddLessons(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = str(error)
        db.Close() 
        return render_template('InsertLessons.html', form=form, message=message)
    db.Close()
    return render_template('InsertLessons.html', form=form, 
                    vTeacher = vTeacher, vSubjects=vSubjects, vGroups=vGroups, vClassrooms=vClassrooms,
                    vLessons=vLessons, message=message)


@app.route('/InsertSubjects', methods=['GET', 'POST'])
@login_required_admin
def InsertSubjects():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = ISubjectsForm()
    message = None
    if form.validate_on_submit():
        vInput = {}
        vInput['name_subject'] = form.subject.data
        try:
            db.AddSubjects(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = str(error)
        
        db.Close()
        return render_template('InsertSubjects.html', form=form, message=message)
    db.Close()
    return render_template('InsertSubjects.html', form=form, message=message)

@app.route('/InsertStudens', methods=['GET', 'POST'])
@login_required_admin
def InsertStudens():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = IStudensForm()
    message = None
    if form.validate_on_submit():
        vInput = {}
        vInput ['id_group'] = form.idGroup.data
        vInput['surname'] = form.surname.data
        vInput['name'] = form.name.data
        vInput['ochestvo'] = form.ochestvo.data
        try:
            db.AddStudens(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vGroups = db.GetGroups( )
        db.Close()
        return render_template('InsertStudens.html', form=form, message=message, 
                                                                    vGroups = vGroups)
    vGroups = db.GetGroups( )
    db.Close()
    return render_template('InsertStudens.html', form=form, 
                                                vGroups=vGroups)


@app.route('/InsertTeachers', methods=['GET', 'POST'])
@login_required_admin
def InsertTeachers():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = ITeachersForm()
    message = None
    if form.validate_on_submit():
        vInput = {}
        vInput['surname'] = form.surname.data
        vInput['name'] = form.name.data
        vInput['ochestvo'] = form.ochestvo.data
        try:
            db.AddTeachers(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        db.Close()
        return render_template('InsertTeachers.html', form=form, message=message)
    db.Close()
    return render_template('InsertTeachers.html', form=form, message=message)

@app.route('/InsertGroups', methods=['GET', 'POST'])
@login_required_admin
def InsertGroups():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = IGroupsForm()
    message = None
    vDepartment = db.GetDepartment()
    if form.validate_on_submit():
        vInput = {}
        vInput['title_group'] = form.groups.data
        vInput['dept_name'] = form.facult.data
        try:
            db.AddGroups(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        db.Close()
        return render_template('InsertGroups.html', form=form, message=message, 
                               vDepartment=vDepartment)
    db.Close()
    return render_template('InsertGroups.html', form=form, message=message, 
                           vDepartment=vDepartment)

@app.route('/InsertDepartment', methods=['GET', 'POST'])
@login_required_admin
def InsertDepartment():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = IDepartmentForm()
    message = None
    if form.validate_on_submit():
        vInput = {}
        vInput['dept_name'] = form.facult.data
        try:
            db.AddDepartment(vInput)
            message = "Запис додано"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        db.Close()
        return render_template('InsertDepartment.html', form=form, message=message)
    db.Close()
    return render_template('InsertDepartment.html', form=form)

@app.route('/InsertClassrooms', methods=['GET', 'POST'])
@login_required_admin
def InsertClassrooms():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = IClassroomsForm()
    if form.is_submitted():
        corpus  = form.corpus.data 
        icorpus = form.icorpus.data
        ncalss  = form.ncalss.data
        try:
            message = "Запис додано"
            if icorpus and corpus and ncalss:
                db.AddCorpus(icorpus)
                db.AddClassroom(corpus, ncalss)
            elif corpus and ncalss:
                db.AddClassroom(corpus, ncalss)
            elif icorpus:
                db.AddCorpus(icorpus)
            else:
                 message = "Недостатньо даних для запису!"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
            vCorpus = db.GetBuilding()
            db.Close()
            return render_template('InsertClassrooms.html', form=form, message = message,
                                                                           vCorpus=vCorpus )
        vCorpus = db.GetBuilding()
        db.Close()
        return render_template('InsertClassrooms.html', form=form, message = message,
                                                                            vCorpus=vCorpus )
    vCorpus = db.GetBuilding()
    db.Close()
    return render_template('InsertClassrooms.html', form=form, vCorpus=vCorpus)
###ENDInsert

###Update
@app.route('/UpdateClassrooms', methods=['GET', 'POST'])
@login_required_admin
def UpdateClassrooms():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = UClassroomsForm()
    if form.is_submitted():
        vInput  = form.corpus.data 
        id = form.icorpus.data
        message = "Запис змінено"
        try:
          db.UpdateClassrooms(vInput,id)
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vCorpus = db.GetBuilding()
        db.Close()
        return render_template('UpdateClassrooms.html', form=form, message = message,
                                                                           vCorpus=vCorpus )
    vCorpus = db.GetBuilding()
    db.Close()
    return render_template('UpdateClassrooms.html', form=form, vCorpus=vCorpus)


@app.route('/UpdateSubjects', methods=['GET', 'POST'])
@login_required_admin
def UpdateSubjects():
    form = USubjectsForm()
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    if form.is_submitted():
        message = ""
        vIdSubjects = form.idS.data
        vInput      = form.subject.data
        try:
            db.UpdateSubjects(vInput, vIdSubjects)
            message = "Запис змінено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vSubjects = db.GetAllSubjects()
        db.Close()
        return render_template('UpdateSubjects.html', form=form, vSubjects=vSubjects, message=message)

    vSubjects = db.GetAllSubjects()
    db.Close()
    return render_template('UpdateSubjects.html', form=form, vSubjects=vSubjects)

@app.route('/UpdateStudens', methods=['GET', 'POST'])
@login_required_admin
def UpdateStudens():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = UStudensForm()
    if form.is_submitted():
        message = ""
        r = []
        for a in request.form.values():
            if a != "":
                r.append(a)
        if len(r) == 2:
            idStudents    = db.GetStudent()
            vGroups       = db.GetGroups()
            db.Close()
            message = "Потрібно обрати хоча б одне поле для зміни!"
            return render_template('UpdateTeachers.html', form=form, 
                     message=message,idStudents=idStudents,vGroups=vGroups)

        vIdStudent                = form.idStudents.data
        vInput = {}
        vInput['surname']         = form.surname.data
        vInput['name']            = form.name.data
        vInput['ochestvo']        = form.ochestvo.data
        vInput['id_group']        = form.idGroup.data
        try:
            db.UpdateStudens(vInput, vIdStudent)
            message = "Запис змінено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        idStudents    = db.GetStudent()
        vGroups       = db.GetGroups()
        db.Close() 
        return render_template('UpdateStudens.html', form=form, 
                              idStudents=idStudents,vGroups=vGroups, message=message)

    idStudents    = db.GetStudent()
    vGroups       = db.GetGroups()
    db.Close()
    return render_template('UpdateStudens.html', form=form, 
                                            idStudents=idStudents,vGroups=vGroups)

@app.route('/UpdateTeachers', methods=['GET', 'POST'])
@login_required_admin
def UpdateTeachers():
    form = UTeachersForm()
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    if form.is_submitted():
        message = ""
        r = []
        for a in request.form.values():
            if a != "":
                r.append(a)
        if len(r) == 2:
            vTeacher    = db.GetAllTeachers()
            db.Close()
            message = "Потрібно обрати хоча б одне поле для зміни!"
            return render_template('UpdateTeachers.html', form=form, 
                    vTeacher = vTeacher, message=message)

        vIdTeachers               = form.idT.data
        vInput = {}
        vInput['surname']         = form.surname.data
        vInput['name']            = form.name.data
        vInput['ochestvo']        = form.ochestvo.data
        try:
            db.UpdateTeachers(vInput, vIdTeachers)
            message = "Запис змінено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vTeacher    = db.GetAllTeachers()
        db.Close() 
        return render_template('UpdateTeachers.html', form=form, 
                    vTeacher = vTeacher, message=message)

    vTeacher    = db.GetAllTeachers()
    db.Close()
    return render_template('UpdateTeachers.html', form=form, vTeacher=vTeacher)

@app.route('/UpdateGroups', methods=['GET', 'POST'])
@login_required_admin
def UpdateGroups():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = UGroupsForm()
    if form.is_submitted():
         message = ""
         r = []
         for a in request.form.values():
            if a != "":
                r.append(a)
         if len(r) == 2:
             vGroups = db.GetGroups()
             vDepartment = db.GetDepartment()
             db.Close()
             message = "Потрібно заповнити хоча б одне поле для зміни!"
             return render_template('UpdateGroups.html', form=form, vGroups=vGroups,
                                    message=message, vDepartment=vDepartment)

         vInput = {}
         vIdGroups  = form.idG.data
         vInput['title_group'] = form.groups.data
         vInput['id_dept'] = form.facult.data
         try:
            db.UpdateGroups(vInput, vIdGroups)
            message = "Запис змінено"
         except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
         vGroups = db.GetGroups()
         vDepartment = db.GetDepartment()
         db.Close()
         return render_template('UpdateGroups.html', form=form, vGroups=vGroups,
                                                             message=message,vDepartment=vDepartment)

    vGroups = db.GetGroups()
    vDepartment = db.GetDepartment()
    db.Close()
    return render_template('UpdateGroups.html', form=form, vGroups=vGroups,
                                                           vDepartment=vDepartment)


@app.route('/UpdateDepartment', methods=['GET', 'POST'])
@login_required_admin
def UpdateDepartment():
    form = UDepartmentForm()
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    if form.is_submitted():
        message = ""
        vIdDepartment = form.idF.data
        vInput       = form.facult.data
        try:
            db.UpdateDepartment(vInput, vIdDepartment)
            message = "Запис змінено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vDepartment   = db.GetDepartment()
        db.Close()
        return render_template('UpdateDepartment.html', form=form, 
                                    vDepartment=vDepartment, message=message)
    vDepartment   = db.GetDepartment()
    db.Close()
    return render_template('UpdateDepartment.html', form=form, vDepartment=vDepartment)

@app.route('/UpdateLessons', methods=['GET', 'POST'])
@login_required_admin
def UpdateLessons():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form        = ULessonsForm()
    if form.is_submitted():
        
        message = ""
        r = []
        for a in request.form.values():
            if a != "":
                r.append(a)
        if len(r) == 2:
            vTeacher    = db.GetAllTeachers()
            vSubjects   = db.GetAllSubjects()
            vGroups     = db.GetGroups()
            vClassrooms = db.GetClassrooms()
            vLessons   = db.GetLesson2()
            db.Close()
            message = "Потрібно обрати хоча б одне поле для зміни!"
            return render_template('UpdateLessons.html', form=form, 
                    vTeacher = vTeacher, vSubjects=vSubjects, vGroups=vGroups, vClassrooms=vClassrooms,
                        vLessons=vLessons, message=message)

        vIdLessons           = form.idL.data
        vInput = {}
        vInput['id_teacher']         = form.teacher.data
        vInput['id_subject']       = form.subject.data
        if form.dateFrom.data:
            vInput['start_date']         = form.dateFrom.data
        else:
            vInput['start_date'] = ""
        if form.dateTo.data:
            vInput['end_date']           = form.dateTo.data
        else:
            vInput['end_date'] = ""

        vInput['id_group']        = form.groups.data
        if form.classroom.data !="": 
            vInput['id_build']   =    form.classroom.data.split('-')[0]
            vInput['number_class']  = form.classroom.data.split('-')[1]
        else : 
            vInput['id_build']     = ""
            vInput['number_class'] = ""
        vInput['para']               = request.form['para']
        vInput['frequency']          = request.form['f']
        vInput['type_lesson']        = request.form['typelesson']
        try:
            db.UpdateLessons(vInput, vIdLessons)
            message = "Запис змінено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vTeacher    = db.GetAllTeachers()
        vSubjects   = db.GetAllSubjects()
        vGroups     = db.GetGroups()
        vClassrooms = db.GetClassrooms()
        vLessons   = db.GetLesson2()
        db.Close() 
        return render_template('UpdateLessons.html', form=form, 
                    vTeacher = vTeacher, vSubjects=vSubjects, vGroups=vGroups, 
                        vClassrooms=vClassrooms, vLessons=vLessons, message=message)
    vTeacher    = db.GetAllTeachers()
    vSubjects   = db.GetAllSubjects()
    vGroups     = db.GetGroups()
    vClassrooms = db.GetClassrooms()
    vLessons   = db.GetLesson2()
    db.Close()
    return render_template('UpdateLessons.html', form=form, 
                    vTeacher = vTeacher, vSubjects=vSubjects, vGroups=vGroups,
                       vClassrooms=vClassrooms, vLessons=vLessons)
###END UPDATE


###Delete
@app.route('/DeleteSubjects', methods=['GET', 'POST'])
@login_required_admin
def DeleteSubjects():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DSubjectsForm()
    if form.is_submitted():
        try:
            vIdSubjects = form.idS.data
            db.DeleteSubjects(vIdSubjects)
            message = "Запис видалено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vSubjects = db.GetAllSubjects()
        db.Close()
        return render_template('DeleteSubjects.html', form=form,
                               vSubjects=vSubjects,message=message)
    vSubjects = db.GetAllSubjects()
    db.Close()
    return render_template('DeleteSubjects.html', vSubjects=vSubjects,
                          form=form)

@app.route('/DeleteStudens', methods=['GET', 'POST'])
@login_required_admin
def DeleteStudens():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DStudensForm()
    if form.is_submitted():
        message = ""
       
        vIdStudent                = form.idStudents.data
        try:
            db.DeleteStudents(vIdStudent)
            message = "Запис видалено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        idStudents    = db.GetStudent()
        db.Close() 
        return render_template('DeleteStudens.html', form=form, 
                              idStudents=idStudents, message=message)

    idStudents    = db.GetStudent()
    db.Close()
    return render_template('DeleteStudens.html', form=form, 
                                            idStudents=idStudents)


@app.route('/DeleteTeachers', methods=['GET', 'POST'])
@login_required_admin
def DeleteTeachers():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DTeachersForm()
    if form.is_submitted():
        message = ""
        vIdTeachers               = form.idT.data
        try:
            db.DeleteTeachers(vIdTeachers)
            message = "Запис видаленно"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vTeacher    = db.GetAllTeachers()
        db.Close() 
        return render_template('DeleteTeachers.html', form=form, 
                    vTeacher = vTeacher, message=message)
    vTeacher    = db.GetAllTeachers()
    db.Close()
    return render_template('DeleteTeachers.html', form=form, vTeacher=vTeacher)
    

@app.route('/DeleteGroups', methods=['GET', 'POST'])
@login_required_admin
def DeleteGroups():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DGroupsForm()
    if form.is_submitted():
         message = ""
         vIdGroups  = form.idG.data
         try:
            db.DeleteGroups(vIdGroups)
            message = "Запис видаленно"
         except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
         vGroups = db.GetGroups()
         db.Close()
         return render_template('DeleteGroups.html', form=form, vGroups=vGroups,
                                                                       message=message)
    vGroups = db.GetGroups()
    db.Close()
    return render_template('DeleteGroups.html', form=form, vGroups=vGroups)

@app.route('/DeleteDepartment', methods=['GET', 'POST'])
@login_required_admin
def DeleteDepartment():
    form = DDepartmentForm()
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    if form.is_submitted():
        message = ""
        vIdDepartment = form.idF.data
        try:
            db.DeleteDepartment(vIdDepartment)
            message = "Запис видалено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vDepartment   = db.GetDepartment()
        db.Close()
        return render_template('DeleteDepartment.html', form=form, 
                                    vDepartment=vDepartment, message=message)
    vDepartment   = db.GetDepartment()
    db.Close()
    return render_template('DeleteDepartment.html', form=form, vDepartment=vDepartment)

@app.route('/DeleteLessons', methods=['GET', 'POST'])
@login_required_admin
def DeleteLessons():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DLessonsForm()
    if form.is_submitted():
        vIdLessons           = form.idL.data
        try:
            db.DeleteLessons(vIdLessons)
            message = "Запис видалено"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
        vLessons   = db.GetLesson2()
        db.Close()
        return render_template('DeleteLessons.html', form=form, vLessons=vLessons, 
                               message=message)
    vLessons   = db.GetLesson2()
    db.Close()
    return render_template('DeleteLessons.html', form=form, vLessons=vLessons)

@app.route('/DeleteClassrooms', methods=['GET', 'POST'])
@login_required_admin
def DeleteClassrooms():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DClassroomsForm()
    if form.is_submitted():
        c = form.c.data
        a = form.a.data
        try:
            message = "Запис видалено"
            if  a:
                corpus   = a.split('-')[0]
                nclass   = a.split('-')[1]
                print("corpus : " + corpus)
                print("ncalss : " + nclass)
            if a and c:
                db.DeleteCorpus(icorpus)
                db.DeleteClassroom(corpus, nclass)
            elif  a:
                db.DeleteClassroom(corpus, nclass)
            elif  c:
                db.DeleteCorpus(icorpus)
            else:
                 message = "Недостатньо даних для видалення!"
        except (Exception, psycopg2.DatabaseError) as error:
            message = "Помилка " + str(error)
            vCorpus = db.GetBuilding()
            vClassrooms = db.GetClassrooms()
            db.Close()
            return render_template('DeleteClassrooms.html', form=form, message = message,
                                                                  vClassrooms = vClassrooms ,vCorpus=vCorpus )
        vCorpus     = db.GetBuilding()
        vClassrooms = db.GetClassrooms()
        db.Close()
        return render_template('DeleteClassrooms.html', form=form, message = message,
                                                  vClassrooms = vClassrooms ,vCorpus=vCorpus )
    vCorpus = db.GetBuilding()
    vClassrooms = db.GetClassrooms()
    db.Close()
    return render_template('DeleteClassrooms.html', form=form,  vClassrooms = vClassrooms, vCorpus=vCorpus)

###END Delete

###ShowTable
@app.route('/ShowClassrooms', methods=['GET', 'POST'])
@login_required
def ShowClassrooms():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vClassrooms   = db.GetClassrooms()
    db.Close()
    return render_template('ShowClassrooms.html', vClassrooms=vClassrooms)

@app.route('/ShowStudens', methods=['GET', 'POST'])
@login_required
def ShowStudens():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vStudens = db.GetStudent()
    return render_template('ShowStudens.html', vStudens=vStudens)

@app.route('/ShowSubjects', methods=['GET', 'POST'])
@login_required
def ShowSubjects():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vSubjects   = db.GetAllSubjects()
    db.Close()
    return render_template('ShowSubjects.html',vSubjects=vSubjects)

@app.route('/ShowGroups', methods=['GET', 'POST'])
@login_required
def ShowGroups():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vGroups   = db.GetGroups()
    db.Close()
    return render_template('ShowGroups.html', vGroups=vGroups)

@app.route('/ShowTeachers', methods=['GET', 'POST'])
@login_required
def ShowTeachers():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vTeachers   = db.GetAllTeachers()
    db.Close()
    return render_template('ShowTeachers.html', vTeachers=vTeachers)

@app.route('/ShowUser', methods=['GET', 'POST'])
@login_required
def ShowUser():
    return render_template('ShowUser.html')

@app.route('/ShowLessons', methods=['GET', 'POST'])
@login_required
def ShowLessons():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vLessons   = db.GetLesson2()
    print(vLessons)
    db.Close()
    return render_template('ShowLessons.html', vLessons = vLessons )

@app.route('/ShowDepartment', methods=['GET', 'POST'])
@login_required
def ShowDepartment():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vDepartment   = db.GetDepartment()
    db.Close()
    return render_template('ShowDepartment.html', vDepartment = vDepartment)
###End ShowTable

@app.route('/ShowInfoGroupSubject', methods=['GET', 'POST'])
@login_required
def ShowInfoGroupSubject():
     try:
        db = SQLqueries()
     except:
        return render_template('Error404.html')
     vGroups = db.GetGroups()
     if request.method == "POST":
        readGroup = request.form['Groups']
        message = ""
        vSubject = db.GetInfoGroupSubject(readGroup)
        message = "Група " + readGroup + " вивчає такі предмети:"
        if not vSubject:
            message = "Групі " + readGroup + " , ще не назначені заняття!"
        db.Close()
        return render_template('ShowInfoGroupSubject.html',
                                    vGroups = vGroups, vSubject = vSubject, message=message)
     db.Close()
     return render_template('ShowInfoGroupSubject.html', 
                                                vGroups = vGroups)

@app.route('/ShowInfoAmountSubjectNextDay', methods=['GET', 'POST'])
@login_required
def ShowInfoAmountSubjectNextDay():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vBuild = db.GetBuild()
    if request.method == "POST":
        readBuild = request.form['Build']
        vAmountSubject = db.GetAmountSubjectInB(readBuild)
        message = "Кількість дисциплін,  які будуть проводити завтра в корпусі "+ readBuild + " дорівнює: "+ str(vAmountSubject[0][0])
        db.Close()
        return render_template('ShowInfoAmountSubjectNextDay.html', message = message, 
                                                                             vBuild = vBuild)
    db.Close()
    return render_template('ShowInfoAmountSubjectNextDay.html', 
                                                    vBuild = vBuild)

@app.route('/ShoWhoHasTwoInDiff', methods=['GET', 'POST'])
@login_required
def ShoWhoHasTwoInDiff():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vListTeachers = db.GetListTeachersInDiffCorps()
    db.Close()
    return render_template('ShoWhoHasTwoInDiff.html', vListTeachers=vListTeachers)

@app.route('/ShowSubjectsWhoGetDiffFucult', methods=['GET', 'POST'])
@login_required
def ShowSubjectsWhoGetDiffFucult():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DateSubjects()
    if form.validate_on_submit():
         vDate    = []
         vDate.append(form.dateFrom.data)
         vDate.append(form.dateTo.data)
         message = None
         if vDate[0] > vDate[1]:
            message = "Дата початку повинна бути меншою за дату кінця!"
            db.Close()
            return render_template('ShowSubjectsWhoGetDiffFucult.html', message=message, form=form)
         VS  = db.GetSubjectsWithDiffFucult(vDate)
         db.Close()
         return render_template('ShowSubjectsWhoGetDiffFucult.html', VS=VS, form=form)

    db.Close()
    return render_template('ShowSubjectsWhoGetDiffFucult.html', form=form)

@app.route('/ShowTeachersMaxCorpus', methods=['GET', 'POST'])
@login_required
def ShowTeachersMaxCorpus():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vListTeachers = db.GetTeacherMaxCorpus()
    db.Close()
    return render_template('ShowTeachersMaxCorpus.html', vListTeachers=vListTeachers)

@app.route('/ShowTeachersWhoHasNowTwoPara', methods=['GET', 'POST'])
@login_required
def ShowTeachersWhoHasNowTwoPara():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    vListTeachers = db.GetTeachersWhoHasNowTwoPara()
    db.Close()
    return render_template('ShowTeachersWhoHasNowTwoPara.html', vListTeachers=vListTeachers)


@app.route('/ShowClassDay', methods=['GET', 'POST'])
@login_required
def ShowClassDay():
    try:
        db = SQLqueries()
    except:
        return render_template('Error404.html')
    form = DayClassroomsForm()
    vClassrooms = db.GetClassrooms()  
    if request.method == "POST":
        V = []
        try:
            t = form.d.data.split('-')
            V.append(t[0])
            V.append(str(t[1]))
            vDay = db.GetD(V)
        except (Exception) as error:
             db.Close()
             return render_template('ShowClassDay.html', message = str(error),
                                   vClassrooms=vClassrooms, form=form)
        db.Close()
        return render_template('ShowClassDay.html', vDay=vDay, 
                               vClassrooms=vClassrooms, form=form)
    db.Close()
    return render_template('ShowClassDay.html',  vClassrooms=vClassrooms, form=form)