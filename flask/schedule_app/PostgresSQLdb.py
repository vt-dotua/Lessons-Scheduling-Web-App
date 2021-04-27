import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, date, time,timedelta
from calendar import monthrange
from copy import deepcopy, copy
from flask import render_template
import os

def CurrentWeek():
    day = date.today()
    day_of_week = day.weekday()
    to_beginning_of_week = timedelta(days=day_of_week)
    beginning_of_week = day - to_beginning_of_week
    to_end_of_week = timedelta(days=6 - day_of_week)
    end_of_week = day + to_end_of_week
    return [beginning_of_week, end_of_week]

def CurrentMonth():
    day = date.today()
    lastDay =  monthrange(day.year, day.month)[1]
    startD  =  str(day.year) + '-' + str(day.month) + '-1'
    endD    =  str(day.year) + '-' + str(day.month) + '-' + str(lastDay)
    start   =  datetime.strptime(startD,   '%Y-%m-%d')
    end     =  datetime.strptime(endD  ,   '%Y-%m-%d')
    return [start, end]
         
class SQLqueries(object):
    def __init__(self):

        DATABASE_NAME = os.getenv("DATABASE_NAME")
        DATABASE_USER = os.getenv("DATABASE_USER")
        DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        DATABASE_PORT = os.getenv("DATABASE_PORT")
        DATABASE_HOST = os.getenv("DATABASE_HOST")

        if DATABASE_NAME is None:
            DATABASE_NAME = "scheduleapp"
        if DATABASE_USER is None: 
            DATABASE_USER = "postgres"
        if DATABASE_PASSWORD is None: 
            DATABASE_PASSWORD = "example"
        if DATABASE_PORT is None: 
            DATABASE_PORT = "5433"
        if DATABASE_HOST is None:
            DATABASE_HOST = "localhost" 

        self.connection = psycopg2.connect(dbname = DATABASE_NAME,
                                           port = DATABASE_PORT,
                                           user = DATABASE_USER, 
                                           password = DATABASE_PASSWORD,
                                           host=DATABASE_HOST,
                                           cursor_factory = DictCursor)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
       

    def Close(self):
        self.cursor.close()
        self.connection.close()
  
    def CheckUser(self, username, password):
        sql = """select 
                    login,
                    password::varchar(256),
                    surname ,
                    name,
                    admin
                 from all_user
                    where login = %s 
                    and
                    password = %s"""
        self.cursor.execute(sql, (username , password) )
        result = self.cursor.fetchall()
        
        return result


    def GetLesson(self, ds, de, select):
            SQL = """select 
	                    gs::date as d_gs,   
	                    l.para,
                        t.surname,
	                    t.name,
                        t.Ochestvo,
	                    g.title_group, 
                        s.name_subject,
	                    l.type_lesson,
	                    b.name_building,
                        l.number_class 
                    from 
	                    Lessons l, 
	                    generate_series(%s, %s, interval '1 day') as gs,
	                    Teachers t,
	                    st_groups g,
	                    subjects s,
	                    building b
                    where 
	                    GET_CUR_LESSON(l.start_date, gs::date, l.end_date, l.frequency) = 1 
                        and
	                    l.id_teacher = t.id_teacher
	                    and l.id_group = g.id_group
	                    and l.id_subject = s.id_subject
	                    and l.id_build = b.id_build
                        and l.id_group = %s
                        order by d_gs, l.para"""
            
            self.cursor.execute(SQL,(str(ds),str(de),select))
            result = self.cursor.fetchall()
            
            dateDic = {}
            if result: 
                dateDic[result[0][0]] = 0
                temp2 = deepcopy(result[0][0])
                for i in range(len(result)):
                    if result[i][0] != temp2:
                        temp2 = result[i][0]
                        dateDic[result[i][0]] = 0

                lis1 = []
                lis2 = []
                k = 0
                for key in dateDic:
                    for i in range(k,len(result)): 
                        for j in range(len(result[i])):
                            if j != 0:
                                lis1.append(copy(result[i][j]))
                        lis2.append(deepcopy(lis1))
                        lis1.clear()
                        if (i + 1) >= len(result):
                            k = i
                            break
                        if key != result[i + 1][0]:
                            k = i + 1
                            break
                    dateDic[key] = deepcopy(lis2)
                    lis2.clear()
            
            return dateDic

    def SingUp(self, login, surname, name, ochestvo, password, email):
            SQL = """
            insert into all_user(login, surname, name, ochestvo, password, email)
                values(%s, %s, %s, %s, sha256(%s), %s)
            """
            self.cursor.execute(SQL, (login, surname, name, ochestvo, password, email))
            pass
            

    def AddLessons(self, vInput):
        #to_date(%s,'yyyy-mm-dd')
        SQL = """insert into Lessons(id_group, id_teacher,  id_subject, para, 
                            type_lesson, id_build, number_class, start_date, end_date, frequency)
                                values(%s, %s, %s, %s , %s,  %s, %s, %s, %s, %s);"""
        
        self.cursor.execute(SQL, (vInput['groups'], vInput['teacher'], vInput['subject'] ,
                                        vInput['para'], vInput['typelesson'], vInput['building'], vInput['classroom'],
                                        vInput['dateFrom'], vInput['dateTo'], vInput['f']))
        pass

    def AddStudens(self, vInput):
        SQL = """ insert into Students(id_group, surname, name, ochestvo) 
                                      values(%s, %s, %s, %s)"""
        self.cursor.execute(SQL,(vInput['id_group'], 
                                 vInput['surname'],vInput['name'],vInput['ochestvo']))
        pass

    def AddSubjects(self, vInput):
        SQL = """insert into subjects(name_subject) values(%s)"""
        self.cursor.execute(SQL,(vInput['name_subject'],))
        pass

    def AddTeachers(self, vInput):
        SQL = """insert into Teachers(surname, name, ochestvo) 
                                values(%s, %s, %s);"""
        self.cursor.execute(SQL,(vInput['surname'], vInput['name'], vInput['ochestvo']))
        pass

    def AddGroups(self, vInput):
        SQL = """insert into st_groups(title_group, id_dept) values(%s,%s)""" 
        self.cursor.execute(SQL, (vInput['title_group'], vInput['dept_name']))
        pass

    def AddDepartment(self, vInput):
        SQL = """insert into Department(dept_name) values(%s)"""
        self.cursor.execute(SQL,(vInput['dept_name'], ))
        pass

    def AddClassroom(self, corpus, icorpus):
        SQL = """insert into classrooms(id_build, number_class) values(%s, %s)"""
        self.cursor.execute(SQL,(corpus,icorpus))
        pass

    def AddCorpus(self, icorpus):
        SQL = """insert into building(name_building) values(%s)"""
        self.cursor.execute(SQL,(icorpus,))
        pass

    def GetBuilding(self):
        sql=""" select * from building"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()
         
    def GetAllTeachers(self):
        sql=""" select id_teacher , surname, name, ochestvo from teachers """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetAllSubjects(self):
        sql = """ select id_subject, name_subject from subjects"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetClassrooms(self):
        sql = """select c.id_build, c.number_class, b.name_building  
                from classrooms c, building b 
                where b.id_build = c.id_build"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetStudent(self):
        sql = """ select 
	                s.id_student,
	                s.surname,
	                s.name,
	                s.ochestvo,
	                g.title_group
                from 
	                students s,
	                st_groups g 
                where s.id_group = g.id_group"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetGroups(self):
        sql = """ select g.id_group, 
	                     g.title_group,
	                     d.dept_name 
                  from
	                     st_groups g,
	                     department d 
                 where g.id_dept = d.id_dept """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetDepartment(self):
        sql = "select * from Department"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetLesson2(self):
        SQL = """select
                    l.id_lesson,
	                g.title_group as group,
	                s.name_subject as subject,
	                l.type_lesson,
	                t.surname || ' ' || substring(t.name, 1, 1)
	                || '.' || substring(t.ochestvo, 1, 1) as teach,
	                b.name_building || '-' || l.number_class as room,
	                l.start_date,
	                l.end_date,
	                l.frequency
                from 
	                lessons l, 
	                st_groups g, 
	                subjects s,
	                teachers t,
	                building b	
               where 
                    l.id_group   = g.id_group
                    and
                    l.id_teacher = t.id_teacher
                    and 
                    l.id_subject = s.id_subject
                    and
                    l.id_build = b.id_build
                    order by l.id_lesson"""
        self.cursor.execute(SQL)
        return self.cursor.fetchall()

    def UpdateLessons(self, vInput, vIdLessons):
        vString = ""
        V = []
        for k, v in vInput.items():
            if str(v) != "":
                vString += str(k) + "= %s,"
                V.append (v)
                print("k = " +  str(k) +  " v = " + str(v))
        vString = vString[:len(vString) - 1]  
        sql = """ update lessons
               set """ + vString + """ 
                    where id_lesson = %s"""
        V.append(vIdLessons)
        print(sql)
        self.cursor.execute(sql, (V))
        pass

    def UpdateStudens(self, vInput, vIdStudent):
        vString = ""
        V = []
        for k, v in vInput.items():
            if str(v) != "":
                vString += str(k) + "= %s,"
                V.append (v)
                print("k = " +  str(k) +  " v = " + str(v))
        vString = vString[:len(vString) - 1]  
        sql = """ update students
               set """ + vString + """ 
                    where id_student = %s"""
        V.append(vIdStudent)
        print(sql)
        self.cursor.execute(sql, (V))
        pass

    def UpdateSubjects(self, vInput, vIdSubjects):
        sql = """ update Subjects
                    set name_subject = %s
                    where id_subject = %s """
        self.cursor.execute(sql, (vInput, vIdSubjects))
        pass

    def UpdateTeachers(self, vInput, vIdTeachers):
        vString = ""
        V = []
        for k, v in vInput.items():
            if str(v) != "":
                vString += str(k) + "= %s,"
                V.append (v)
                print("k = " +  str(k) +  " v = " + str(v))
        vString = vString[:len(vString) - 1]  
        sql = """ update teachers
               set """ + vString + """ 
                    where id_teacher = %s"""
        V.append(vIdTeachers)
        print(sql)
        self.cursor.execute(sql, (V))
        pass

    def UpdateGroups(self, vInput, vIdGroups):
        vString = ""
        V = []
        for k, v in vInput.items():
            if str(v) != "":
                vString += str(k) + "= %s,"
                V.append (v)
                print("k = " +  str(k) +  " v = " + str(v))
        vString = vString[:len(vString) - 1]  
        sql = """ update st_groups
               set """ + vString + """ 
                    where id_group = %s"""
        V.append(vIdGroups)
        print(sql)
        self.cursor.execute(sql, (V))
        pass

    def UpdateDepartment(self, vInput, vIdDepartment):
        sql = """ update Department
                    set dept_name = %s
                    where id_dept = %s """
        self.cursor.execute(sql, (vInput, vIdDepartment))
        pass

    def UpdateClassrooms(self, vInput, id):
        sql = """ update Building
                    set name_building = %s
                    where id_build  = %s """
        
        self.cursor.execute(sql, (vInput, id))
        pass

    def DeleteLessons(self, vIdLessons):
        sql = """ delete from lessons 
                    where id_lesson = %s """
        self.cursor.execute(sql, (vIdLessons,))
        pass

    def DeleteSubjects(self, vIdSubjects):
        sql = """ delete from Subjects 
                    where id_subject = %s """
        self.cursor.execute(sql, (vIdSubjects,))
        pass
    
    def DeleteTeachers(self, vIdTeachers):
        sql = """ delete from Teachers 
                    where id_teacher = %s """
        self.cursor.execute(sql, (vIdTeachers,))
        pass

    def DeleteGroups(self, vIdGroups):
        sql = """ delete from st_groups 
                    where id_group = %s """
        self.cursor.execute(sql, (vIdGroups,))
        pass
         
    def DeleteDepartment(self, vIdDepartment):
        sql = """ delete from Department 
                    where id_dept = %s """
        self.cursor.execute(sql, (vIdDepartment,))
        pass

    def DeleteStudents(self, vIdStudent):
        sql = """ delete from Students 
                    where id_student = %s """
        self.cursor.execute(sql, (vIdStudent,))
        pass

    def GetInfoGroupSubject(self, vGroup):
        sql = """ select distinct  
	                    s.name_subject 
                  from 
	                    lessons l, 
	                    subjects s,
	                    st_groups g
                 where 
                        s.id_subject = l.id_subject
                        and g.id_group = l.id_group
                        and g.title_group = %s 
                        and CURRENT_DATE <= end_date"""
        self.cursor.execute(sql, (vGroup, ))
        return self.cursor.fetchall()

    def GetAmountSubjectInB(self, vBuild):
        sql = """
                select
	            count(
		            DISTINCT
  		                l.id_subject) 
                from 
	               Lessons l, 
	               building b
                where 
	                GET_CUR_LESSON(l.start_date, 
				            CURRENT_DATE + 1, l.end_date, l.frequency) = 1
	                and l.id_build   = b.id_build 
	                AND b.name_building = %s"""
        self.cursor.execute(sql, (vBuild, ))
        return self.cursor.fetchall()

    def GetBuild(self):
        sql = """ select * from building """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def GetListTeachersInDiffCorps(self):
        sql = """ select distinct t.id_teacher, t.surname, t.name, t.ochestvo from(
	                    select
		                    gs::date,
		                    l.id_teacher,
		                    l.para,
		                    l.id_build
	                    from 
		                    Lessons l,
		                    generate_series(%s, %s, interval '1 day') as gs
	                    where  
		                    GET_CUR_LESSON(l.start_date, gs::date, l.end_date, l.frequency) = 1
	                        order by gs ,l.id_teacher, l.para
                        ) as l, teachers t
                     where 
                        l.id_teacher in (select id_teacher from Lessons  where 
                                             GET_CUR_LESSON(start_date, l.gs::date, end_date, frequency) = 1 
				                             and id_teacher = l.id_teacher 
				                             and para = l.para+1 
				                             and id_build != l.id_build)
                                             and t.id_teacher = l.id_teacher"""
        self.cursor.execute(sql, CurrentWeek())
        return self.cursor.fetchall()
    def GetSubjectsWithDiffFucult(self, vDate):
        sql = """select
	                s.name_subject
                from 
	               Lessons l,
	               subjects s,
	               st_groups g,
	              generate_series(%s, %s, interval '1 day') as gs
              where  
	               l.id_group = g.id_group
	               and s.id_subject = l.id_subject
	               and GET_CUR_LESSON(start_date, gs::date, end_date, frequency) = 1
                   group by s.name_subject
	               having count(distinct g.id_dept) > 1;
             """
        self.cursor.execute(sql, vDate)
        return self.cursor.fetchall()

    def GetTeacherMaxCorpus(self):
        sql = """ select  t.id_teacher, t.surname, t.name, t.ochestvo, l.count_building from(
	                    select 
	                        l.id_teacher,
		                    l.count_building,
		                    max(l.count_building) OVER () as r_max
	                    from(
		                    select
			                    l.id_teacher,
			                    count(distinct l.id_build) as count_building
		                    from 
			                    Lessons l,
			                    generate_series(%s, %s, interval '1 day') as gs
		                    where  
			                    GET_CUR_LESSON(l.start_date, gs::date, l.end_date, l.frequency) = 1
		                        group by l.id_teacher
	                    	) as l
                 ) as l,teachers t  where l.count_building = l.r_max and t.id_teacher = l.id_teacher"""

        self.cursor.execute(sql, CurrentMonth())
        return self.cursor.fetchall()

    def GetTeachersWhoHasNowTwoPara(self):
        sql = """ select distinct t.id_teacher, t.surname, t.name, t.ochestvo from(
	                    select
		                    gs::date,
		                    l.id_teacher,
		                    l.para,
	                        l.number_class,
		                    l.id_build
	              from 
		                 Lessons l,
		                 generate_series('2019-04-22', '2019-04-27', interval '1 day') as gs
	              where  
		                 GET_CUR_LESSON(l.start_date, gs::date, l.end_date, l.frequency) = 1
	                     order by gs ,l.id_teacher, l.para
                 ) as l, teachers t
                 where 
                        l.id_teacher in (select id_teacher from Lessons  where 
                        GET_CUR_LESSON(start_date, l.gs::date, end_date, frequency) = 1 
				        and id_teacher = l.id_teacher 
				        and para = l.para 
				        and (id_build != l.id_build
				        or number_class  != l.number_class))
                        and t.id_teacher = l.id_teacher"""
        self.cursor.execute(sql, CurrentWeek())
        return self.cursor.fetchall()

    def DeleteCorpus(self, icorpus):
        sql = """delete from building 
                        where id_build = %s"""
        self.cursor.execute(sql, (icorpus,))
        pass

    def DeleteClassroom(self, corpus, nclass):
        sql = """delete from classrooms 
                        where id_build = %s and number_class = %s"""
        self.cursor.execute(sql, (corpus, nclass))
        pass

    def CheckEmail(self, email):
        sql = """select 
                    email
                 from all_user
                    where email = %s 
                    """
        self.cursor.execute(sql, (email,))
        return self.cursor.fetchall()

    def ChangePassword(self, email, password):
        sql = """ update all_user 
                  set password = sha256(%s)
                  where email = %s
                  """
        print("password = " + password)
        print("email = " + email)
        self.cursor.execute(sql, (password, email))
        pass

    def GetD(self, V):
        sql = """
                    select to_char(l.start_date,'Day') 
	                        from lessons l, building b
                    where l.id_build = b.id_build
                    EXCEPT
                    select to_char(l.start_date,'Day')
	                    from lessons l, building b  
		            where l.id_build = b.id_build 
	 	            and b.name_building = %s 
		            and l.number_class = %s;

                """ 
        self.cursor.execute(sql, V)
        return self.cursor.fetchall()

#try:
##except (Exception, psycopg2.DatabaseError) as error:
