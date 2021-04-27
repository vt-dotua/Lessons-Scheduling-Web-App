create database scheduleapp;
\c scheduleapp;

CREATE TABLE all_User (
  Id_user  serial NOT NULL UNIQUE,
  Surname  varchar(40) NOT NULL, 
  Name     varchar(40) NOT NULL,
  Ochestvo varchar(40) NOT NULL, 
  password bytea NOT NULL, 
  email    varchar(100) NOT NULL UNIQUE, 
  login    varchar(50) NOT NULL UNIQUE,  
  admin    bool, 
  PRIMARY KEY (Id_user));

CREATE TABLE Building (
  id_build      serial NOT NULL UNIQUE, 
  name_building varchar(10), 
  PRIMARY KEY (id_build));

CREATE TABLE Classrooms (
  number_class int4 NOT NULL, 
  id_build     int4 NOT NULL, 
  PRIMARY KEY (number_class, 
  id_build));

CREATE TABLE Department (
  id_dept   serial NOT NULL UNIQUE, 
  Dept_name varchar(40) NOT NULL UNIQUE, 
  PRIMARY KEY (id_dept));

CREATE TABLE Lessons (
  id_lesson    serial NOT NULL UNIQUE, 
  id_group     int4 NOT NULL, 
  id_teacher   int4 NOT NULL, 
  para         int2 NOT NULL, 
  id_subject   int4 NOT NULL,  
  type_lesson  varchar(20), 
  number_class int4 NOT NULL, 
  id_build     int4 NOT NULL, 
  start_date   date NOT NULL, 
  end_date     date NOT NULL, 
  frequency    int4 NOT NULL,  
  CONSTRAINT id_lesson 
    PRIMARY KEY (id_lesson));

CREATE TABLE st_Groups (
  id_group    serial NOT NULL UNIQUE, 
  title_group varchar(20) NOT NULL UNIQUE, 
  id_dept     int4, 
  PRIMARY KEY (id_group));

CREATE TABLE Students (
  Id_student  serial NOT NULL UNIQUE, 
  id_group    int4 NOT NULL, 
  Name        varchar(50) NOT NULL, 
  Surname     varchar(50) NOT NULL, 
  Ochestvo    varchar(50) NOT NULL, 
  PRIMARY KEY (Id_student));

CREATE TABLE Subjects (
  id_subject   serial NOT NULL UNIQUE, 
  name_subject varchar(40) NOT NULL UNIQUE, 
  PRIMARY KEY (id_subject));

CREATE TABLE Teachers (
  Id_teacher serial NOT NULL UNIQUE, 
  Name       varchar(40) NOT NULL, 
  Surname    varchar(50) NOT NULL, 
  Ochestvo   varchar(50) NOT NULL, 
  PRIMARY KEY (Id_teacher));

ALTER TABLE Students ADD CONSTRAINT r_1 FOREIGN KEY (id_group) REFERENCES st_Groups (id_group);
ALTER TABLE Lessons ADD CONSTRAINT r_2 FOREIGN KEY (id_group) REFERENCES st_Groups (id_group);
ALTER TABLE Lessons ADD CONSTRAINT r_3 FOREIGN KEY (id_subject) REFERENCES Subjects (id_subject);
ALTER TABLE Lessons ADD CONSTRAINT r_4 FOREIGN KEY (id_teacher) REFERENCES Teachers (Id_teacher);
ALTER TABLE st_Groups ADD CONSTRAINT r_5 FOREIGN KEY (id_dept) REFERENCES Department (id_dept);
ALTER TABLE Lessons ADD CONSTRAINT r_6 FOREIGN KEY (number_class, id_build) REFERENCES Classrooms (number_class, id_build);
ALTER TABLE Classrooms ADD CONSTRAINT r_7 FOREIGN KEY (id_build) REFERENCES Building (id_build);

CREATE OR REPLACE FUNCTION fmod (
   dividend double precision,
   divisor double precision
) RETURNS double precision
    LANGUAGE sql IMMUTABLE AS
'SELECT dividend - floor(dividend / divisor) * divisor';

CREATE OR REPLACE FUNCTION GET_CUR_LESSON( start_date in date, curdate in date, end_date in date ,frequency in int4 ) 
RETURNS int4 as 
$$
DECLARE
	v_r int4;
BEGIN 
  IF  fmod((curdate - start_date)::float /7, frequency) = 0 and curdate <= end_date
  then 
    V_R := 1;
  ELSE
    V_R := 0;
  END IF;
  return v_r;
END;
$$
LANGUAGE 'plpgsql';

--- Триггер для проверки, чтоб для одной группы на одно и тоже время не было 2 пары
CREATE OR REPLACE FUNCTION chack_lasson() returns trigger as 
$$
declare
c integer;
begin

if NEW.start_date > NEW.end_date then
  RAISE EXCEPTION 'Дата початку повинна бути меншою за дату кінця!';
end if;

select count(*) into c from Lessons l 
	where GET_CUR_LESSON(l.start_date, NEW.start_date, l.end_date, l.frequency) = 1 
	and l.para = NEW.para
	and l.id_group = NEW.id_group;

if c > 0 then
	RAISE EXCEPTION 'Пара в цей час уже назначена!';
  
end if;
return NEW;
end
$$ LANGUAGE plpgsql;

create trigger chak_l before 
insert or update on lessons 
for each row execute procedure chack_lasson();
---

insert into all_user(surname,name,ochestvo,login, password, admin, email) 
       values ('admin', 'admin', 'admin','admin' , sha256('12345'), true, 'admin@admin.com');

--Department
insert into Department(dept_name) values('ЕЛІТ');  -- 1    
insert into Department(dept_name) values('ТЕСЕТ'); -- 2    
insert into Department(dept_name) values('ІФСК');  -- 3   
      
--Building
insert into building(name_building) values('ЕТ'); -- 1   
insert into building(name_building) values('М');  -- 2       
insert into building(name_building) values('Н');  -- 3  

--Classrooms 
insert into classrooms(id_build, number_class) values(1, 100);
insert into classrooms(id_build, number_class) values(1, 101);
insert into classrooms(id_build, number_class) values(1, 102);
insert into classrooms(id_build, number_class) values(1, 103);
insert into classrooms(id_build, number_class) values(1, 104);
insert into classrooms(id_build, number_class) values(1, 105);
insert into classrooms(id_build, number_class) values(1, 106);
insert into classrooms(id_build, number_class) values(1, 107);
insert into classrooms(id_build, number_class) values(1, 108);
insert into classrooms(id_build, number_class) values(1, 109);
insert into classrooms(id_build, number_class) values(1, 110);

insert into classrooms(id_build, number_class) values(2, 100);
insert into classrooms(id_build, number_class) values(2, 101);
insert into classrooms(id_build, number_class) values(2, 102);
insert into classrooms(id_build, number_class) values(2, 103);
insert into classrooms(id_build, number_class) values(2, 104);
insert into classrooms(id_build, number_class) values(2, 105);
insert into classrooms(id_build, number_class) values(2, 106);
insert into classrooms(id_build, number_class) values(2, 107);
insert into classrooms(id_build, number_class) values(2, 108);
insert into classrooms(id_build, number_class) values(2, 109);
insert into classrooms(id_build, number_class) values(2, 110);

insert into classrooms(id_build, number_class) values(3, 100);
insert into classrooms(id_build, number_class) values(3, 101);
insert into classrooms(id_build, number_class) values(3, 102);
insert into classrooms(id_build, number_class) values(3, 103);
insert into classrooms(id_build, number_class) values(3, 104);
insert into classrooms(id_build, number_class) values(3, 105);
insert into classrooms(id_build, number_class) values(3, 106);
insert into classrooms(id_build, number_class) values(3, 107);
insert into classrooms(id_build, number_class) values(3, 108);
insert into classrooms(id_build, number_class) values(3, 109);
insert into classrooms(id_build, number_class) values(3, 110);
--
--st_Groups 
insert into st_groups(title_group, id_dept) values('КБ-61',1);
insert into st_groups(title_group, id_dept) values('ІМ-81',2);  
insert into st_groups(title_group, id_dept) values('ЖТ-71',3); 

--students
insert into students(id_group, surname, name, ochestvo) 
  values(1, 'Борисенко', 'Микола' , 'Максимович');
insert into students(id_group, surname, name, ochestvo) 
  values(1, 'Стусенко', 'Сергій' , 'Вадимович');
insert into students(id_group, surname, name, ochestvo) 
  values(1, 'Огієнко', 'Світлана' , 'Володимірівна');
insert into students(id_group, surname, name, ochestvo) 
  values(2, 'Цимбалюк', 'Яна' , 'Миколаївна');
insert into students(id_group, surname, name, ochestvo) 
  values(2, 'Ткаченко', 'Ірина' , 'Анатоліївна');
insert into students(id_group, surname, name, ochestvo) 
  values(2, 'Морозко', 'Ірина' , 'Степанівна');

--Subjects 
insert into subjects(name_subject) values('WEB-безпека');                       -- 1                        
insert into subjects(name_subject) values('JAVA');                              -- 2                               
insert into subjects(name_subject) values('C++');                               -- 3                                
insert into subjects(name_subject) values('C#');                                -- 4                                 
insert into subjects(name_subject) values('Операційні системи');                -- 5                 
insert into subjects(name_subject) values('LINUX');                             -- 6                              
insert into subjects(name_subject) values('Бази даних');                        -- 7                         
insert into subjects(name_subject) values('Стеганографія');                     -- 8                      
insert into subjects(name_subject) values('Дискретна математика');              -- 9               
insert into subjects(name_subject) values('Вища математика');                   -- 10                    
insert into subjects(name_subject) values('Криптографія');                      -- 11                       
insert into subjects(name_subject) values('Англійська мова');                   -- 12                    
insert into subjects(name_subject) values('Обслуговування ПК');                 -- 13                  
insert into subjects(name_subject) values('ТСПП');                              -- 14                               
insert into subjects(name_subject) values('Числені методи');                    -- 15                     
insert into subjects(name_subject) values('Мат. логіка');                       -- 16                        
insert into subjects(name_subject) values('Телекомунікації');                   -- 17                    
insert into subjects(name_subject) values('Теорія алгоритмів');                 -- 18                  
insert into subjects(name_subject) values('Мат. методи');                       -- 19                        
insert into subjects(name_subject) values('Забезпечення якісної інф.');         -- 20          
insert into subjects(name_subject) values('Інформац. техніка');                 -- 21          
insert into subjects(name_subject) values('Властивості матеріалів');            -- 22         
insert into subjects(name_subject) values('Основи електротехніки');             -- 23         
insert into subjects(name_subject) values('Охорона праці');                     -- 24         
insert into subjects(name_subject) values('Економіка підприємств');             -- 25         
insert into subjects(name_subject) values('Дослідження операцій');              -- 26         
insert into subjects(name_subject) values('Випадкові процеси');                 -- 27         
insert into subjects(name_subject) values('Методи багатовимірної статистики');  -- 28 
insert into subjects(name_subject) values('Теорія керування');                  -- 29                   
insert into subjects(name_subject) values('Рівняння математ. фізики');          -- 30              
insert into subjects(name_subject) values('Теорія ймовірн. та мат. стат.');     -- 31      
insert into subjects(name_subject) values('Теорія функц. дійсн. змінної');      -- 32       
insert into subjects(name_subject) values('Методи наукових обчислень');         -- 33              
insert into subjects(name_subject) values('Історія');                           -- 34                            
insert into subjects(name_subject) values('Укр. мова');                         -- 35                          
insert into subjects(name_subject) values('Методи журналістів');                -- 36                 
insert into subjects(name_subject) values('Основи журналістики');               -- 37                
insert into subjects(name_subject) values('Сучасний медіатекст');               -- 38                
insert into subjects(name_subject) values('Історія публіцистики');              -- 39               
insert into subjects(name_subject) values('Укр. мов ЗМІ');                      -- 40                       
insert into subjects(name_subject) values('Професійна етика та медіоправо');    -- 41         
insert into subjects(name_subject) values('Деталі машин');                      -- 42 
insert into subjects(name_subject) values('Взаєм., станд., та техн.вимір');     -- 43 
insert into subjects(name_subject) values('Теор.основи теплотехніки');          -- 44 
insert into subjects(name_subject) values('Фізичне виховання');                 -- 45 
insert into subjects(name_subject) values('Економічний аналіз');                -- 46 
insert into subjects(name_subject) values('Економіка праці');                   -- 47 
insert into subjects(name_subject) values('Інф. системи в економ.');            -- 48 
insert into subjects(name_subject) values('Ділова іноземна мова');              -- 49 
insert into subjects(name_subject) values('Економетрика');                      -- 50 
insert into subjects(name_subject) values('Теорія різання');                    -- 51 
insert into subjects(name_subject) values('Ріжучий інструмент');                -- 52 
insert into subjects(name_subject) values('Бізнес рішення');                    -- 53 
insert into subjects(name_subject) values('Орг. інновац. діяльн');              -- 54 
insert into subjects(name_subject) values('Start-UP');                          -- 55 
insert into subjects(name_subject) values('Планування та бюджетобудування');    -- 56 
insert into subjects(name_subject) values('Основи сцен-режисерскої дій.');      -- 57 
insert into subjects(name_subject) values('Івент менеджмент');                  -- 58 
insert into subjects(name_subject) values('Ентопсихологія');                    -- 59 
insert into subjects(name_subject) values('Історія мистества');                 -- 60 
insert into subjects(name_subject) values('Іміджелогія та брендинг');           -- 61 
insert into subjects(name_subject) values('Регіональні практики з соц-кул');    -- 62 

--Teachers
insert into Teachers(surname, name, ochestvo)        -- 1  
  values('Драган', 'Надій', 'Найденович');
insert into Teachers(surname, name, ochestvo)        -- 2  
  values('Вакалюк', 'Вселюб', 'Златович');  
insert into Teachers(surname, name, ochestvo)        -- 3   
  values('Довгаль', 'Гуляйвітер', 'Богуславович');
insert into Teachers(surname, name, ochestvo)        -- 4
  values('Куновський', 'Вітомир', 'Соломонович');
insert into Teachers(surname, name, ochestvo)        -- 5
  values('Чуприна', 'Матвій', 'Іванович');
insert into Teachers(surname, name, ochestvo)        -- 6
  values('Андрусів', 'Ніка', 'Гордиславівна');
insert into Teachers(surname, name, ochestvo)        -- 7
  values('Авратинська', 'Шанетта', 'Тарасівна');
insert into Teachers(surname, name, ochestvo)        -- 8
  values('Штанько', 'Еммануїла', 'Милославівна');
insert into Teachers(surname, name, ochestvo)        -- 9
  values('Шаблій', 'Зореслава', 'Артурівна');
insert into Teachers(surname, name, ochestvo)        -- 10
  values('Сліпченко', 'Чесмил', 'Леонідович');
insert into Teachers(surname, name, ochestvo)        -- 11
  values('Трух', 'Юхим', 'Жданович');
insert into Teachers(surname, name, ochestvo)        -- 12
  values('Юрчишин', 'Єремій', 'Юхимович');
insert into Teachers(surname, name, ochestvo)        -- 13
  values('Саніна', 'Емма', 'Устимівна');
insert into Teachers(surname, name, ochestvo)        -- 14
  values('Мацько', 'Шарлота', 'Максимівна');
insert into Teachers(surname, name, ochestvo)        -- 15
  values('Пилипчук', 'Чеслава', 'Федорівна');
insert into Teachers(surname, name, ochestvo)        -- 16
  values('Бернацька', 'Огняна', 'Давидівна');
insert into Teachers(surname, name, ochestvo)        -- 17
  values('Арсенич', 'Йоган', 'Янович');
insert into Teachers(surname, name, ochestvo)        -- 18
  values('Пасенюк', 'Іван', 'Макарович');

--Lessons 
--Пары для КБ-61
insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    1,                 -- преподаватель
    14,                -- предмет
    1,                 -- номер пары
    'Лекція',          -- тип занятия
    3,                 -- корпус 
    101,               -- номер аудитории
    CURRENT_DATE - 27, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    2,                 -- преподаватель
    1,                 -- предмет
    2,                 -- номер пары
    'Практика',          -- тип занятия
    3,                 -- корпус 
    104,               -- номер аудитории
    CURRENT_DATE - 27, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

  insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    3,                 -- преподаватель
    12,                -- предмет
    3,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    106,               -- номер аудитории
    CURRENT_DATE - 27, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    3,                 -- преподаватель
    12,                -- предмет
    3,                 -- номер пары
    'Лекція',        -- тип занятия
    1,                 -- корпус 
    107,               -- номер аудитории
    CURRENT_DATE - 26, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    3,                 -- преподаватель
    24,                -- предмет
    4,                 -- номер пары
    'Лекція',        -- тип занятия
    2,                 -- корпус 
    105,               -- номер аудитории
    CURRENT_DATE - 26, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    5,                 -- преподаватель
    7,                 -- предмет
    1,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    101,               -- номер аудитории
    CURRENT_DATE - 26, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    5,                 -- преподаватель
    7,                 -- предмет
    2,                 -- номер пары
    'Лекція',        -- тип занятия
    2,                 -- корпус 
    104,               -- номер аудитории
    CURRENT_DATE - 26, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    7,                 -- преподаватель
    11,                 -- предмет
    1,                 -- номер пары
    'Практика',        -- тип занятия
    2,                 -- корпус 
    102,               -- номер аудитории
    CURRENT_DATE - 25, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    7,                 -- преподаватель
    11,                -- предмет
    2,                 -- номер пары
    'Лекція',          -- тип занятия
    2,                 -- корпус 
    102,               -- номер аудитории
    CURRENT_DATE - 25, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    1,                 -- преподаватель
    6,                 -- предмет
    3,                 -- номер пары
    'Практика',        -- тип занятия
    2,                 -- корпус 
    102,               -- номер аудитории
    CURRENT_DATE - 25, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    1,                 -- преподаватель
    6,                -- предмет
    1,                 -- номер пары
    'Лекція',          -- тип занятия
    2,                 -- корпус 
    102,               -- номер аудитории
    CURRENT_DATE - 24, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    2,                 -- номер пары
    'Лекція',          -- тип занятия
    1,                 -- корпус 
    101,               -- номер аудитории
    CURRENT_DATE - 24, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    1,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 23, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    2,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 23, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    10,                -- преподаватель
    12,                -- предмет
    3,                 -- номер пары
    'Лекція',        -- тип занятия
    2,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 23, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    1,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 22, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    10,                -- преподаватель
    12,                -- предмет
    3,                 -- номер пары
    'Лекція',        -- тип занятия
    2,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 22, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    1,                 -- преподаватель
    6,                -- предмет
    1,                 -- номер пары
    'Лекція',          -- тип занятия
    2,                 -- корпус 
    102,               -- номер аудитории
    CURRENT_DATE - 21, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    2,                 -- номер пары
    'Лекція',          -- тип занятия
    1,                 -- корпус 
    101,               -- номер аудитории
    CURRENT_DATE - 21, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

insert into
  Lessons(
    id_group,
    id_teacher,
    id_subject,
    para,
    type_lesson,
    id_build,
    number_class,
    start_date,
    end_date,
    frequency
  )
values(
    1,                 -- группа
    9,                 -- преподаватель
    8,                 -- предмет
    3,                 -- номер пары
    'Практика',        -- тип занятия
    3,                 -- корпус 
    109,               -- номер аудитории
    CURRENT_DATE - 21, -- дата начала предмета
    CURRENT_DATE + 60, -- дата окончания предмета
    1                  -- повторение
  );

--Lessons 
--Пары для ІМ-61
