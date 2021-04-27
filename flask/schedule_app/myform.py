from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.fields.html5 import DateTimeLocalField, DateField,EmailField 
from wtforms.validators import DataRequired,InputRequired, Email, Length 

class LoginForm(FlaskForm):
    username = StringField("І'мя користувача", validators = [InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=4, max=50)])

class RegisterForm(FlaskForm):
    username = StringField("І'мя користувача", validators = [InputRequired(), Length(min=4, max=15)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    surname = StringField('Призвище', validators = [InputRequired(), Length(min=4, max=15)])
    name = StringField("І'мя", validators = [InputRequired(), Length(min=4, max=15)])
    ochestvo = StringField("Ім'я по батькові", validators = [InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=4, max=50)])

class DateForm(FlaskForm):
    dateFrom = DateField("З", format='%Y-%m-%d', validators = [InputRequired()])
    dateTo   = DateField("До", format='%Y-%m-%d', validators = [InputRequired()])

class ILessonsForm(FlaskForm):
      teacher  = StringField('Оберіть викладача', validators = [InputRequired()], render_kw={"list" : "t"})
      groups   = StringField('Оберіть групу', validators = [InputRequired()],   render_kw={"list" : "g"})
      subject  = StringField('Оберіть предмет', validators = [InputRequired()], render_kw={"list" : "s"})
      classroom  = StringField('Оберіть аудиторію', validators = [InputRequired()], render_kw={"list" : "c"})
      dateFrom = DateField("Дата початку", format='%Y-%m-%d', validators = [InputRequired()])
      dateTo   = DateField("Дата кінця", format='%Y-%m-%d', validators = [InputRequired()])

class ITeachersForm(FlaskForm):
    surname = StringField('Призвище', validators = [InputRequired(), Length(min=4, max=15)])
    name = StringField("І'мя", validators = [InputRequired(), Length(min=4, max=15)])
    ochestvo = StringField("Ім'я по батькові", validators = [InputRequired(), Length(min=4, max=15)])

class IStudensForm(FlaskForm):
    surname = StringField('Призвище', validators = [InputRequired(), Length(min=4, max=15)])
    name = StringField("І'мя", validators = [InputRequired(), Length(min=4, max=15)])
    ochestvo = StringField("Ім'я по батькові", validators = [InputRequired(), Length(min=1, max=15)])
    idGroup = StringField("Оберіть групу", validators = [InputRequired(), Length(min=1, max=15)], render_kw={"list" : "ig"})

class ISubjectsForm(FlaskForm):
    subject = StringField('Назва предмета', validators = [InputRequired(), Length(min=1, max=15)])

class IGroupsForm(FlaskForm):
    groups = StringField('Назва групи', validators = [InputRequired(), Length(min=1, max=15)])
    facult = StringField('Назва факультету', validators = [InputRequired(), Length(min=1, max=15)]
                                                           , render_kw={"list" : "f"})

class IClassroomsForm(FlaskForm):
    corpus  =  StringField('Оберіть корпусу', render_kw={"list" : "ik"})
    icorpus =  StringField('Назва корпусу')
    ncalss  =  StringField("Номер аудиторії")

class IDepartmentForm(FlaskForm):
    facult = StringField('Назва факультету', validators = [InputRequired(), Length(min=1, max=15)])

class UClassroomsForm(FlaskForm):
    icorpus  =  StringField('Оберіть корпусу', validators = [InputRequired(), Length(min=1, max=15)],  render_kw={"list" : "ik"})
    corpus =   StringField('Введіть нову назву корпусу', validators = [InputRequired(), Length(min=1, max=15)])
   
class UStudensForm(FlaskForm):
    surname = StringField('Призвище', validators = [Length(min=4, max=15)])
    name = StringField("І'мя", validators = [Length(min=4, max=15)])
    ochestvo = StringField("Ім'я по батькові", validators = [Length(min=1, max=15)])
    idGroup = StringField("Оберіть групу", validators = [Length(min=1, max=15)], render_kw={"list" : "ig"})
    idStudents = StringField("Оберіть студента", validators = [Length(min=1, max=15)], render_kw={"list" : "is"})


class ULessonsForm(FlaskForm):
      idL      = StringField('Оберіть заняття, для зміни', validators = [InputRequired()], render_kw={"list" : "il"})
      teacher  = StringField('Оберіть викладача',   render_kw={"list" : "t"})
      groups   = StringField('Оберіть групу',       render_kw={"list" : "g"})
      subject  = StringField('Оберіть предмет',     render_kw={"list" : "s"})
      classroom  = StringField('Оберіть аудиторію', render_kw={"list" : "c"})
      dateFrom = DateField("Дата початку", format='%Y-%m-%d')
      dateTo   = DateField("Дата кінця", format='%Y-%m-%d')

class UTeachersForm(FlaskForm):
    idT     =  StringField('Оберіть викладача, для зміни', validators = [InputRequired()], render_kw={"list" : "it"})
    surname = StringField('Призвище',  validators = [Length(min=4, max=25)])
    name = StringField("І'мя",  validators = [Length(min=4, max=25)])
    ochestvo = StringField("Ім'я по батькові",  validators = [Length(min=4, max=25)])

class USubjectsForm(FlaskForm):
    idS     = StringField('Оберіть предмет, для зміни', validators = [InputRequired()], render_kw={"list" : "is"})
    subject = StringField('Назва предмета', validators = [InputRequired(), Length(min=1, max=15)])

class UGroupsForm(FlaskForm):
    idG    = StringField('Оберіть групу, для зміни', validators = [InputRequired()], render_kw={"list" : "ig"})
    groups = StringField('Назва групи', validators = [Length(min=1, max=15)])
    facult = StringField('Назва факультету', validators = [Length(min=1, max=15)]
                                                           , render_kw={"list" : "f"})

class UDepartmentForm(FlaskForm):
    idF    = StringField('Оберіть факультет, для зміни', validators = [InputRequired()], render_kw={"list" : "if"})
    facult = StringField('Назва факультету', validators = [InputRequired(), Length(min=1, max=15)])

class DLessonsForm(FlaskForm):
      idL      = StringField('Оберіть заняття, для видалення', validators = [InputRequired()], render_kw={"list" : "il"})

class DSubjectsForm(FlaskForm):
    idS     = StringField('Оберіть предмет, для видалення', validators = [InputRequired()], render_kw={"list" : "is"})

class DTeachersForm(FlaskForm):
    idT     =  StringField('Оберіть викладача, для видалення', validators = [InputRequired()], render_kw={"list" : "it"})
   
class DGroupsForm(FlaskForm):
    idG    = StringField('Оберіть групу, для видалення', validators = [InputRequired()], render_kw={"list" : "ig"})
   
class DDepartmentForm(FlaskForm):
    idF    = StringField('Оберіть факультет, для видалення', validators = [InputRequired()], render_kw={"list" : "if"})
    
class DStudensForm(FlaskForm):
    idStudents = StringField("Оберіть студента, для видалення", validators = [Length(min=1, max=15)], render_kw={"list" : "is"})

class DateSubjects(FlaskForm):
    dateFrom = DateField("Дата початку", format='%Y-%m-%d', validators = [InputRequired()])
    dateTo   = DateField("Дата кінця", format='%Y-%m-%d', validators = [InputRequired()])

class DClassroomsForm(FlaskForm):
    a = StringField("Оберіть аудиторію", validators = [Length(min=1, max=15)], render_kw={"list" : "ia"})
    c = StringField("Оберіть корпус",    validators = [Length(min=1, max=15)], render_kw={"list" : "ic"})

class MyEmail(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])

class ChangePassword(FlaskForm):
      password = PasswordField('Введіть новий пароль', validators=[InputRequired(), Length(min=4, max=50)])

class DayClassroomsForm(FlaskForm):
    d = StringField("Оберіть аудиторію", validators = [InputRequired(), Length(min=1, max=15)], render_kw={"list" : "id"})