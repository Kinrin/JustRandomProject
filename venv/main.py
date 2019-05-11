from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import imageio
import re
from random import shuffle
from decimal import Decimal
from PIL import ImageTk, Image
from pathlib import Path
import os, subprocess
import moviepy.editor as mp
from moviepy.editor import VideoFileClip
from winsound import *
from playsound import playsound
import time
import threading
import datetime
import collections

def check():
    def destrik():
        win.destroy()
        db.close()
        os.remove("mydb")
        root.destroy()

    login = message.get()
    lgn=[(login,)]
    pas=message2.get()
    password = [(message2.get(),)]

    cursor.execute('''SELECT * FROM Usr WHERE login=? ''', (login,))
    result=cursor.fetchall()
    cursor.execute('''SELECT * FROM Teach WHERE login=? ''', (login,))
    teach=cursor.fetchall()
    if result:

        cursor.execute('''SELECT password FROM Usr WHERE login=?''', (login,))
        pswr = cursor.fetchall()

        if(pswr == password):
            student(login)
            root.withdraw()

        else:
            messagebox.showinfo('Вы ошиблись!', 'Вы ввели не верный пароль!')
    elif teach:

        cursor.execute('''SELECT password FROM Teach WHERE login=?''', (login,))
        pswr = cursor.fetchall()

        if(pswr == password):
            teacher(login)
            root.withdraw()
        else:
            messagebox.showinfo('Вы ошиблись!', 'Вы ввели не верный пароль!')
    else:
        messagebox.showinfo('Вы ошиблись!','Такой логин не зарегестрирован!')



globflag = FALSE

def teacher(login):
    def ex():
        teach_win.destroy()
        root.update()
        root.deiconify()

    def otchet_course(fio, course, studak):
        def backo():
            otch_win.destroy()
            list_of_students(course)
        cursor.execute('''SELECT adress FROM ''' + course + ''' WHERE type=?''', ("test",))
        names_of_tests = cursor.fetchall()
        cursor.execute('''SELECT stud_info_table FROM list_of_courses WHERE name=?''', (course,))
        name_stud_table = cursor.fetchall()[0][0]
        cursor.execute('''SELECT №_stud FROM ''' + name_stud_table)
        stds = cursor.fetchall()

        otch_win = Toplevel();
        otch_win.title("Просмотр отчёт по курсу")
        otch_win.geometry("1000x100")
        easy = []
        hard = []
        for j in range(len(stds)):
            for i in range(len(names_of_tests)):
                cursor.execute('''SELECT DISTINCT link FROM ''' + names_of_tests[i][0])
                lks = cursor.fetchall()
                link =[]
                for y in range(len(lks)):
                    link.append(lks[y][0])
                wrongs =[]
                all_answ = []
                cursor.execute('''SELECT ''' + names_of_tests[i][0] + ''' FROM ''' + name_stud_table + '''  WHERE №_stud=?''', (stds[j][0],))
                tmp_r = cursor.fetchall()[0][0]
                ratings = []
                if (tmp_r):
                    ratings = tmp_r.split()
                    ratings.reverse()
                    rr = len(ratings) / 2
                    ids = []
                    rating = []
                    for r in range(int(rr)):
                        id = ratings.pop()
                        rtg = ratings.pop()
                        ids.append(id)
                        rating.append(rtg)
                    for k in range(len(link)):
                        wrongs.append(0)
                        all_answ.append(0)
                    for k2 in range(len(link)):
                        cursor.execute('''SELECT id FROM ''' + names_of_tests[i][0] + '''  WHERE link=?''', (link[k2],))
                        tmp_id = cursor.fetchall()
                        for t in range(len(tmp_id)):
                            temp = ids.index(str(tmp_id[t][0]))
                            ocenka = rating[temp]
                            if (ocenka == "0"):
                                wrong_answ = wrongs[k2]
                                wrong_answ +=1
                                wrongs[k2]= wrong_answ
                                a_answ = all_answ[k2]
                                a_answ += 1
                                all_answ[k2] = a_answ
                            else:
                                a_answ = all_answ[k2]
                                a_answ += 1
                                all_answ[k2] = a_answ
                    for ab in range(len(wrongs)):
                        trew = (wrongs[ab]/all_answ[ab]) * 100
                        if( trew > 67):
                            hard.append(link[ab])
                        elif (trew < 10):
                            easy.append(link[ab])
        h = [item for item, count in collections.Counter(hard).items() if count > 1]
        e = [item for item, count in collections.Counter(easy).items() if count > 1]
        hh=[]
        ee=[]
        for m in range(len(h)):
            cursor.execute('''SELECT name FROM ''' + course + '''  WHERE id=?''', (h[m],))
            tmph = cursor.fetchall()[0][0]
            hh.append(tmph)
        for n in range(len(e)):
            cursor.execute('''SELECT name FROM ''' + course + '''  WHERE id=?''', (e[n],))
            tmpe = cursor.fetchall()[0][0]
            ee.append(tmpe)
        Label(otch_win,text="Список наиболее сложных жлементов курса = " + str(hh)).grid( row= 0, column = 0)
        Label(otch_win, text="Список наиболее простых жлементов курса = " + str(ee)).grid(row=1, column=0)
        Button(otch_win, text='Назад', command=backo).grid(row=2, column=0)
    def test_info(fio,course,studak):

        def back():
            test_info_win.destroy()
            infot(fio,course,studak)
        cursor.execute('''SELECT adress FROM '''+ course +''' WHERE type=?''', ("test",))
        names_of_tests = cursor.fetchall()
        cursor.execute('''SELECT stud_info_table FROM list_of_courses WHERE name=?''', (course,))
        name_stud_table = cursor.fetchall()[0][0]

        test_info_win = Toplevel();
        test_info_win.title("Просмотр результатов ответов на тесты")
        test_info_win.geometry("600x230")

        tree = ttk.Treeview(test_info_win)
        tree["columns"] = ("one", "two")
        tree.column("#0", width=150, minwidth=100,)
        tree.column("one", width=150, minwidth=100)
        tree.column("two", width=150, minwidth=100)

        tree.heading("#0", text="Название Теста" )
        tree.heading("one", text="id вопроса")
        tree.heading("two", text="Ответ")
        c = 1
        for t in range(len(names_of_tests)):
            tmp = names_of_tests[t][0]
            cursor.execute('''SELECT ''' + tmp + ''' FROM ''' + name_stud_table + '''  WHERE №_stud=?''', (studak,))
            tmp_r = cursor.fetchall()[0][0]
            ratings =[]
            if(tmp_r):
                ratings = tmp_r.split()
                ratings.reverse()
                rr = len(ratings)/2
                ids = []
                rating = []
                for r in range(int(rr)):
                    id = ratings.pop()
                    rtg = ratings.pop()
                    ids.append(id)
                    rating.append(rtg)
                for i in range(len (ids)):
                    tree.insert("",c,text = tmp,values =(ids[i],"Правильный" if rating[i] == "1" else "Ошибка"))
                    c+=1

        scrollbar = Scrollbar(test_info_win, command=tree.yview())
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky=W, rowspan=3)
        scrollbar.grid(row=0, column=1, sticky=N + S + W, rowspan=3)

        Button(test_info_win, text='Назад', command=back).grid(row=1, column=2)



    def infot(fio,course,studak):
        def back():
            info_win.destroy()
            list_of_students(course)
        def test_info_go(fio,course,studak):
            test_info(fio,course, studak)
            info_win.destroy()

        info_win = Toplevel();
        info_win.title("Просмотр информации по выбранному курсу")
        info_win.geometry("950x230")

        cursor.execute('''SELECT individual_trajectory FROM MathStud WHERE №_stud=?''', (studak,))
        in_tr = cursor.fetchall()

        cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
        time = cursor.fetchall()[0][0]
        times = time.split()

        cursor.execute('''SELECT progress FROM MathStud WHERE №_stud=?''', (studak,))
        progres = cursor.fetchall()[0][0]

        cursor.execute('''SELECT rating FROM MathStud WHERE №_stud=?''', (studak,))
        rating = cursor.fetchall()[0][0]
        ratings = rating.split()
        ratings.reverse()
        it_l = in_tr[0][0].split()
        names = []
        types = []
        for el in it_l:
            cursor.execute('''SELECT name FROM MathCourse WHERE id=?''', (el,))
            tmp_el = cursor.fetchall()
            names.append(tmp_el)

            cursor.execute('''SELECT type FROM MathCourse WHERE id=?''', (el,))
            tmp_el = cursor.fetchall()
            types.append(tmp_el)

        tree = ttk.Treeview(info_win)
        tree["columns"] = ("one", "two", "three", "four")
        tree.column("#0", width=250, minwidth=150, )
        tree.column("one", width=150, minwidth=150)
        tree.column("two", width=150, minwidth=150)
        tree.column("three", width=80, minwidth=50)
        tree.column("four", width=80, minwidth=50)

        tree.heading("#0", text="Название")
        tree.heading("one", text="Тип материала")
        tree.heading("two", text="Затраченное время")
        tree.heading("three", text="Пройден")
        tree.heading("four", text="Оценка")
        for i in range(len(names)):
            if (i != len(types) - 1):
                if (types[i][0][0] == "test" and len(ratings) != 0):
                    tmp = ratings.pop()
                else:
                    tmp = " "
            else:
                if (types[i][0][0] == "test" and len(ratings) != 0):
                    tmp = ratings.pop()
                else:
                    tmp = " "
            tree.insert("", i + 1, text=names[i][0][0],
                        values=(types[i], times[i] if i < len(times) else "0", "+" if i < len(times) else "-", tmp))
        scrollbar = Scrollbar(info_win, command=tree.yview())
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky=W, rowspan=3)
        scrollbar.grid(row=0, column=1, sticky=N + S + W, rowspan=3)
        progressbar = ttk.Progressbar(info_win, orient="horizontal", mode="determinate")
        progressbar.grid(row=0, column=2)
        progressbar["value"] = len(times)
        progressbar["maximum"] = len(names)

        cur = it_l[len(times)] if len(it_l) > len(times) else it_l[len(it_l) - 1]
        it_l.reverse()

        Button(info_win, text='Отчёт по тестам', command=lambda: test_info_go(fio, course, studak)).grid(row=1, column=2)
        Button(info_win, text='Назад', command=back).grid(row=2, column=2)




    def list_of_students(var):
        def back_l():
            s_win.destroy()
            list_of_courses_teacher(studak)

        def goto_l(fio,var):
            s_win.destroy()
            cursor.execute('''SELECT №_stud FROM Usr WHERE fio = ? ''', (fio,))
            stu = cursor.fetchall()[0][0]
            infot(fio,var,stu)

        def otchet(fio,var):
            s_win.destroy()
            cursor.execute('''SELECT №_stud FROM Usr WHERE fio = ? ''', (fio,))
            stu = cursor.fetchall()[0][0]
            otchet_course(fio,var,stud)
        s_win = Toplevel()
        s_win.title("Просмотр студентов записанных на выбранный курс")
        s_win.geometry("350x150")
        Label(s_win, text="Выберите студента информацию о котором вы хотите получить:").grid(row = 0,column = 0)
        cursor.execute('''SELECT id FROM Usr ''')
        ids = [item[0] for item in cursor.fetchall()]
        cursor.execute('''SELECT id FROM list_of_courses WHERE name = ? ''', (var,))
        name_id = cursor.fetchall()[0][0]
        list_of_ids = []
        for id in ids:
            cursor.execute('''SELECT list_courses FROM Usr WHERE id = ? ''', (id,))
            li = cursor.fetchall()[0][0]
            lis = li.split()
            if(str(name_id) in lis):
                cursor.execute('''SELECT fio FROM Usr WHERE id = ? ''', (id,))
                list_of_ids.append(cursor.fetchall()[0][0])

        variable = StringVar(s_win)
        variable.set(list_of_ids[0])


        cou = var
        w = OptionMenu(s_win, variable, *list_of_ids).grid(row = 1,column = 0,rowspan=2)
        var = variable.get()

        Button(s_win, text='Информация по выбранному курсу', command=lambda: goto_l(variable.get(),cou)).grid(row = 3,column = 0)
        Button(s_win, text='Отчёт по курсу', command=lambda: otchet(variable.get(), cou)).grid(row = 4,column = 0)
        Button(s_win, text='Назад', command=back_l).grid(row = 5,column = 0)


    def list_of_courses_teacher(studak):
        def back():
            list_win.destroy()
            win.update()
            win.deiconify()

        def goto(var, num):
            list_win.destroy()
            list_of_students(var)

        list_win = Toplevel()
        list_win.title("просмотр курсов преподавателя")
        list_win.geometry("300x150")


        Label(list_win, text="Выберите студента информацию о котором вы хотите получить:").pack()

        cursor.execute('''SELECT list_courses FROM Teach WHERE №_stud=?''', (studak,))
        lc = cursor.fetchall()

        list_courses = lc[0][0]
        lst = list_courses.split()
        l = []

        for course in lst:
            cursor.execute('''SELECT name FROM list_of_courses WHERE id=?''', (course,))
            tmp = cursor.fetchall()
            l.append(tmp[0][0])
        teach_win.withdraw()


        variable = StringVar(list_win)
        variable.set(l[0])

        w = OptionMenu(list_win, variable, *l).place(relx=.3, rely=.15)
        var = variable.get()
        Button(list_win, text='Информация по выбранному курсу', command=lambda: goto(variable.get(), studak)).place(
            relx=.15, rely=.45)
        Button(list_win, text='Назад', command=back).place(relx=.4, rely=.75)
    teach_win = Toplevel()
    teach_win.title("Главное окно преподавателя")
    teach_win.geometry("250x100")
    cursor.execute('''SELECT fio FROM Teach WHERE login=?''', (login,))
    name_of_teacher = cursor.fetchall()

    mess = "Добро пожаловать, " + name_of_teacher[0][0]
    Label(teach_win, text=mess).grid(row =0 , column = 0,rowspan = 2)

    cursor.execute('''SELECT №_stud FROM Teach WHERE login=?''', (login,))
    stud = cursor.fetchall()
    Button(teach_win, text='Просмотр курсов', command=lambda: list_of_courses_teacher(stud[0][0])).grid( row = 2,column= 0,rowspan = 2)
    Button(teach_win, text='Выйти', command=ex).grid(row = 4 , column =0,rowspan = 2)
def student(login):
    def ex():
        win.destroy()
        root.update()
        root.deiconify()

    def learning(choosen_course,studak,individual_trajectory, current_element,info_var):

        def testform(choosen_course,studak,individual_trajectory, cur, i = 0,rez = "", now = time.strftime("%H:%M:%S")):
            def update_clock(new,label,test_win):
                now = time.strftime("%H:%M:%S")
                n = datetime.datetime.strptime(now, "%H:%M:%S") - datetime.datetime.strptime(new, "%H:%M:%S")
                label.configure(text=n)
                test_win.after(1000, update_clock,new,label,test_win)
            def nexttest(inext,var,true,rez,now):
                if(var != "NULL"):
                    if( var == true):
                        rez += str(int(inext)) + " 1 "
                        test_win.destroy()
                        testform(choosen_course, studak, individual_trajectory, cur, inext,rez,now)
                    else:
                        push = int(inext)
                        rez += str(push) + " 0 "
                        test_win.destroy()
                        testform(choosen_course, studak, individual_trajectory, cur, inext, rez,now)
                else:
                    messagebox.showinfo('Ошибка', 'Выберите ответ!')
            def finish(rez,n,var,true,inext):
                if (var != "NULL"):
                    if (var == true):
                        rez += " "+ str(int(inext)) + " 1 "
                    else:
                        push = int(inext)
                        rez += str(push) + " 0 "

                def add_last(curent_element,f_l):
                    cursor.execute('SELECT individual_trajectory FROM MathStud WHERE №_stud=?', (studak,))
                    it = cursor.fetchall()[0][0]
                    final_link = " "+f_l+" "
                    global globflag
                    pos = it.find(str(final_link))
                    if(current_element == "1" and globflag == FALSE):
                        new = it[:pos+2] +" " + current_element + it[pos+2:]
                        globflag = TRUE
                    else:
                        tmp = it[:pos+1] + it[pos+2:]
                        pos2 = tmp.find(str(final_link))
                        if(pos2<0):
                            new = it[:pos + 2] + " " + current_element + it[pos + 2:]
                        else:
                            left = tmp[:pos2 + 2]
                            nl = left[:pos] + final_link + left[pos:]
                            right = tmp[pos2 + 2:]
                            new = nl + " " + current_element + " " + right
                    cursor.execute('UPDATE MathStud SET individual_trajectory = \'' + new + '\' WHERE №_stud=?',
                                   (studak,))
                    db.commit()






                cursor.execute('UPDATE MathStud SET '+ name_of_test +' = \''+ rez +'\' WHERE №_stud=?', (studak,))
                db.commit()
                list_to_analyze = rez.split()
                list_to_analyze.reverse()
                chk = len(list_to_analyze)/2;
                plus = 0;
                all = 0;
                wrong_id = 0
                final_link = 0
                cer = current_element
                flag = FALSE
                for i in range(int(chk)*2 - 1,-1,-2):
                    id = list_to_analyze[i]
                    result = list_to_analyze[i-1]
                    if result == "1":
                        plus += 1
                        all += 1
                    else:
                        all += 1
                procent = (plus / all) * 100
                for l in range (int(chk)) :
                    id = list_to_analyze.pop()
                    result = list_to_analyze.pop()

                    print(id+" "+result)
                    cursor.execute('SELECT link FROM ' + name_of_test + ' WHERE id = ?', (id,))
                    link = cursor.fetchall()[0][0]
                    if result != "1":
                    #     plus+=1
                    #     all+=1
                    # else:
                    #     all+=1
                        if procent >= 50:
                            if wrong_id != link:
                                wrong_id = link
                            else:
                                cursor.execute('SELECT individual_trajectory FROM MathStud WHERE №_stud=?', (studak,))
                                it = cursor.fetchall()[0][0]
                                pos = it.find(cer)
                                sho = it[:pos] + it[pos + 2:]
                                ps = sho.find(" "+current_element+" ")
                                if (ps>0):
                                    pp = int(ps)+1
                                    tmp = it[:pp+3]+ " "+link + it[pp + 3:]
                                    print(tmp)
                                    cursor.execute('UPDATE MathStud SET individual_trajectory = \'' + tmp + '\' WHERE №_stud=?',(studak,))
                                    db.commit()
                                else:
                                    left = it[:pos+2]
                                    right = it[pos+2:]
                                    if(int(cer)>9):
                                        new = left + " "+ link + " " + right
                                    else:
                                        new = left +  link+ " " + right
                                    cursor.execute('UPDATE MathStud SET individual_trajectory = \'' + new + '\' WHERE №_stud=?', (studak,))
                                    db.commit()
                                final_link = link
                                wrong_id = 0
                                cer = link
                                flag = TRUE


                if(int(procent) < 50):
                    info(info_var, studak)
                    messagebox.showinfo('Конец!', 'Тест не сдан попробуйте ещё раз!')
                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 0"

                    test_win.destroy()
                elif ( int(procent) == 50):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 25"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?',(studak,))
                    db.commit()
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 25')
                    if( flag == TRUE):
                        add_last(current_element,final_link)
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) > 50 and int(procent) <= 60):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 30"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    if (flag == TRUE):
                        add_last(current_element, final_link)
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 30')
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) > 60 and int(procent) <= 70):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 35"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    if (flag == TRUE):
                        add_last(current_element, final_link)
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 35')
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) > 70 and int(procent) <= 80):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 40"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    if (flag == TRUE):
                        add_last(current_element, final_link)
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 40')
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) > 70 and int(procent) <= 80):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 45"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    if (flag == TRUE):
                        add_last(current_element, final_link)
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 45')
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) > 80 and int(procent) <= 99):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 50"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    if (flag == TRUE):
                        add_last(current_element, final_link)
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 50')
                    test_win.destroy()
                    info(info_var, studak)
                elif (int(procent) >=100 and int(procent) <= 100):

                    n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                    sec = n_time.time().second
                    ms = n_time.time().minute
                    hs = n_time.time().hour
                    m = int(ms) * 60
                    h = int(hs) * 3600
                    total = int(sec) + m + h

                    cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                    time = cursor.fetchall()[0][0]
                    tim = time + " " + str(total)
                    cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                    db.commit()

                    cursor.execute('SELECT rating FROM MathStud WHERE №_stud=?', (studak,))
                    rating = cursor.fetchall()[0][0]
                    rtgs = rating + " 54"
                    cursor.execute('UPDATE MathStud SET rating = \'' + rtgs + '\' WHERE №_stud=?', (studak,))
                    db.commit()
                    messagebox.showinfo('Конец!', 'Тест  сдан оценка - 54')
                    test_win.destroy()
                    info(info_var, studak)

            cursor.execute('SELECT adress FROM MathCourse WHERE id=?', (cur,))
            name_of_test = cursor.fetchall()[0][0]
            cursor.execute('''SELECT id FROM ''' + name_of_test + ''' ''')
            tp = cursor.fetchall()
            list_of_vars = []
            test_win = Toplevel()
            test_win.title("Тест")
            test_win.geometry("350x250")
            cursor.execute('''SELECT name FROM ''' + name_of_test + ''' WHERE id=?''', (tp[i][0],))
            question = cursor.fetchall()[0][0]
            cursor.execute('''SELECT truevar FROM ''' + name_of_test + ''' WHERE id=?''', (tp[i][0],))
            true = cursor.fetchall()[0][0]
            list_of_vars.append(true)
            cursor.execute('''SELECT nottruevar1 FROM ''' + name_of_test + ''' WHERE id=?''', (tp[i][0],))
            list_of_vars.append(cursor.fetchall()[0][0])
            cursor.execute('''SELECT nottruevar2 FROM ''' + name_of_test + ''' WHERE id=?''', (tp[i][0],))
            list_of_vars.append(cursor.fetchall()[0][0])
            cursor.execute('''SELECT nottruevar3 FROM ''' + name_of_test + ''' WHERE id=?''', (tp[i][0],))
            list_of_vars.append(cursor.fetchall()[0][0])
            shuffle(list_of_vars)
            S = Scrollbar(test_win)
            T = Text(test_win, width=40,height = 5)
            S.grid(row=0, column=1, sticky='NSW', rowspan=3)
            T.grid(row=0, column=0, sticky='E', rowspan=3)
            S.config(command=T.yview)
            T.config(yscrollcommand=S.set)
            T.insert(END, question)
            T.config(state=DISABLED)

            v = StringVar()
            v.set("NULL")
            ir = 3
            for q in list_of_vars:
                b = Radiobutton(test_win, text=q,
                                variable=v, value=q)
                b.grid(row = str(ir), column = 0)
                ir+=1

            label_clock = Label(test_win, text="")
            label_clock.grid(row=ir + 1, column=0)
            async_update_thread = threading.Thread(target=update_clock,
                                                   args=(now, label_clock, test_win,))
            async_update_thread.start()
            Button(test_win, text='Следующий вопрос' if  len(tp) > i+1 else "Завершить тест", command=lambda: nexttest(i+1,v.get(),true,rez,now) if len(tp) > i+1 else finish(rez,label_clock.cget("text"),v.get(),true,i+1)).grid(row=ir, column=0)


        def video_choice():
            def update_clock(new,label,learning_win):
                now = time.strftime("%H:%M:%S")
                n = datetime.datetime.strptime(now, "%H:%M:%S") - datetime.datetime.strptime(new, "%H:%M:%S")
                label.configure(text=n)
                learning_win.after(1000, update_clock,new,label,learning_win)
            def ex(n):

                learning_win.destroy()
                info(choosen_course,studak)
            def next(n):
                n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                sec = n_time.time().second
                ms = n_time.time().minute
                hs = n_time.time().hour
                m = int(ms) * 60
                h = int(hs) * 3600
                total = int(sec) + m + h

                cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                time = cursor.fetchall()[0][0]
                tim = time + " " + str(total)
                cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                db.commit()
                learning_win.destroy()

                if (len(individual_trajectory) > 0):
                    ce = individual_trajectory.pop()
                    learning(choosen_course, studak, individual_trajectory, str(ce),info_var)
                else:
                    messagebox.showinfo('Конец!', 'Изучение курса закончено!')
            cursor.execute('''SELECT video_adress FROM MathCourse WHERE id=?''', (current_element,))
            adr = cursor.fetchall()[0][0]
            cursor.execute('''SELECT path FROM list_of_courses WHERE name=?''', (choosen_course,))
            path_to_course = cursor.fetchall()[0][0]

            video = imageio.get_reader(adr)
            delay = int(1000 / video.get_meta_data()['fps'])

            def stream(label):
                try:
                    image = video.get_next_data()
                except:
                    video.close()
                    return
                label.after(delay, lambda: stream(label))
                frame_image = ImageTk.PhotoImage(Image.fromarray(image))
                label.config(image=frame_image)
                label.image = frame_image

            learning_win = Toplevel()
            learning_win.title("Изучение курса")
            learning_win.geometry("800x370")

            my_label = Label(learning_win)
            my_label.grid(row=1, column=1, rowspan=3)
            my_label.after(delay, lambda: stream(my_label))

            cursor.execute('''SELECT name FROM MathCourse WHERE id=?''', (current_element,))
            tmp = cursor.fetchall()



            now = time.strftime("%H:%M:%S")
            label_clock = Label(learning_win, text="")
            label_clock.grid(row=2, column=4)
            async_update_thread = threading.Thread(target=update_clock,args=(now, label_clock, learning_win,))
            async_update_thread.start()

            Button(learning_win, text='Следующий материал', command=lambda: next(label_clock.cget("text"))).grid(row=1, column=4)
            Button(learning_win, text='Закончить изучение', command=lambda: ex(label_clock.cget("text"))).grid(row=3, column=4)
        def text_choice():
            def update_clock_text(new,label,learning_win_text):
                now = time.strftime("%H:%M:%S")
                n = datetime.datetime.strptime(now,"%H:%M:%S") - datetime.datetime.strptime(new,"%H:%M:%S")
                label.configure(text=n)
                learning_win_text.after(1000, update_clock_text, new,label,learning_win_text)
            def extext(n):
                learning_win_text.destroy()
                info(choosen_course,studak)
            def nexttext(n):
                learning_win_text.destroy()
                n_time = datetime.datetime.strptime(n, "%H:%M:%S")
                sec = n_time.time().second
                ms = n_time.time().minute
                hs = n_time.time().hour
                m = int(ms) * 60
                h = int(hs) * 3600
                total = int(sec) + m + h

                cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
                time = cursor.fetchall()[0][0]
                tim = time + " " + str(total)
                cursor.execute('UPDATE MathStud SET time_to_element = \'' + tim + '\' WHERE №_stud=?', (studak,))
                db.commit()

                if (len(individual_trajectory) > 0):
                    ce = individual_trajectory.pop()
                    learning(choosen_course, studak, individual_trajectory, str(ce),info_var)
                else:
                    messagebox.showinfo('Конец!', 'Изучение курса закончено!')
                    learning_win_text.destroy()
                    info(info_var,studak)


            learning_win_text = Toplevel()
            learning_win_text.title("Изучение курса")
            learning_win_text.geometry("650x370")

            cursor.execute('''SELECT adress FROM MathCourse WHERE id=?''', (current_element,))
            adr = cursor.fetchall()[0][0]
            cursor.execute('''SELECT path FROM list_of_courses WHERE name=?''', (choosen_course,))
            path_to_course = cursor.fetchall()[0][0]

            with open(adr, 'r') as file:
                data = file.read()
            S = Scrollbar(learning_win_text)
            T = Text(learning_win_text, width=50)

            S.grid(row=0,column=1,sticky='NSW',rowspan=3)
            T.grid(row=0,column=0,sticky = 'E',rowspan=3)
            S.config(command=T.yview)
            T.config(yscrollcommand=S.set)
            T.insert(END, data)
            T.config(state=DISABLED)

            now = time.strftime("%H:%M:%S")
            label_clock = Label(learning_win_text, text="")
            label_clock.grid(row=1, column=2)
            async_update_thread = threading.Thread(target=update_clock_text, args=(now,label_clock,learning_win_text,))
            async_update_thread.start()

            Button(learning_win_text, text='Следующий материал', command=lambda: nexttext( label_clock.cget("text"))).grid(row=0, column=2)
            Button(learning_win_text, text='Закончить изучение', command=lambda: extext( label_clock.cget("text"))).grid(row=2, column=2)

        cursor.execute('''SELECT type FROM MathCourse WHERE id=?''', (current_element,))
        tp = cursor.fetchall()[0][0]
        if(tp== "test"):
            if(len(individual_trajectory)>0):

                testform(choosen_course,studak,individual_trajectory,current_element)
            elif (len(individual_trajectory)==0):
                testform(choosen_course, studak, individual_trajectory, current_element)
            else:
                messagebox.showinfo('Конец!', 'Изучение курса закончено!')
        else:
            cursor.execute('''SELECT format FROM MathStud WHERE №_stud=?''', (studak,))
            format = cursor.fetchall()[0][0]
            if(format == "video"):
                text_choice()
            else :
                text_choice()
                print("text")

    def info(var,studak):
        def back():
            info_win.destroy()
            list_of_courses_student(studak)
        def golearn(choosen_course,studak,individual_trajectory, current_element):
            learning(choosen_course, studak, individual_trajectory, current_element,var)
            info_win.destroy()
        def analyze_format():
            cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
            ttm = cursor.fetchall()[0][0].split()
            if(ttm):
                ttm_avg = sum(list(map(int, ttm))) / float(len(ttm))
            else:
                ttm_avg = 0

            cursor.execute('''SELECT adress FROM MathCourse WHERE type =?''', ("test",))
            adresses = cursor.fetchall()
            cursor.execute('''SELECT format FROM MathStud WHERE №_stud=?''', (studak,))
            format = cursor.fetchall()[0][0]
            count_loses = 0
            all_count = 0
            for l in range (len(adresses)):
                name_test = adresses[l][0]
                cursor.execute('''SELECT DISTINCT link FROM ''' + name_test )
                links_id = cursor.fetchall()
                cursor.execute('''SELECT '''+ name_test + ''' FROM MathStud WHERE №_stud =?''', (studak,))
                test_answers = cursor.fetchall()[0][0]
                if(test_answers):
                    count_loses += test_answers.count(" 0 ")
                    ta = test_answers.split()
                    all_count += len(ta)/2
                else:
                    count_loses+=1
                    all_count+=1

            if ((count_loses/int(all_count))*100 < 50 and ttm_avg <60):
                if ( format == "text"):
                    cursor.execute('''UPDATE MathStud SET format = 'video' WHERE №_stud =?''', (studak,))
                else:
                    cursor.execute('''UPDATE MathStud SET format = 'text' WHERE №_stud =?''', (studak,))

            cursor.execute('''SELECT format FROM MathStud WHERE №_stud=?''', (studak,))
            print(cursor.fetchall()[0][0])


        info_win = Toplevel();
        info_win.title("Просмотр информации по выбранному курсу")
        info_win.geometry("950x230")

        cursor.execute('''SELECT individual_trajectory FROM MathStud WHERE №_stud=?''', (studak,))
        in_tr = cursor.fetchall()

        cursor.execute('''SELECT time_to_element FROM MathStud WHERE №_stud=?''', (studak,))
        time = cursor.fetchall()[0][0]
        times = time.split()


        cursor.execute('''SELECT progress FROM MathStud WHERE №_stud=?''', (studak,))
        progres = cursor.fetchall()[0][0]


        cursor.execute('''SELECT rating FROM MathStud WHERE №_stud=?''', (studak,))
        rating = cursor.fetchall()[0][0]
        ratings = rating.split()
        ratings.reverse()
        it_l = in_tr[0][0].split()
        names = []
        types = []
        for el in it_l:

            cursor.execute('''SELECT name FROM MathCourse WHERE id=?''', (el,))
            tmp_el = cursor.fetchall()
            names.append(tmp_el)

            cursor.execute('''SELECT type FROM MathCourse WHERE id=?''', (el,))
            tmp_el = cursor.fetchall()
            types.append(tmp_el)

        tree = ttk.Treeview(info_win)
        tree["columns"] = ("one", "two", "three", "four")
        tree.column("#0", width=250, minwidth=150,)
        tree.column("one", width=150, minwidth=150)
        tree.column("two", width=150, minwidth=150)
        tree.column("three", width=80, minwidth=50)
        tree.column("four", width=80, minwidth=50)

        tree.heading("#0", text="Название")
        tree.heading("one", text="Тип материала")
        tree.heading("two", text="Затраченное время")
        tree.heading("three", text="Пройден")
        tree.heading("four", text="Оценка")

        for i in range (len(names)):
            if (i != len(types)-1):
                if (types[i][0][0] == "test" and len(ratings)!= 0):
                    tmp = ratings.pop()
                else:
                    tmp = " "
            else:
                if (types[i-1][0][0] == "test" and len(ratings) != 0):
                    tmp = ratings.pop()
                else:
                    tmp = " "
            tree.insert("", i+1, text=names[i][0][0], values=(types[i], times[i] if i < len(times) else "0", "+" if i < len(times) else "-", tmp))
        scrollbar = Scrollbar(info_win, command=tree.yview())
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid( row =0, column = 0, sticky = W, rowspan = 3)
        scrollbar.grid(row =0, column = 1, sticky=N+S+W, rowspan = 3)
        progressbar = ttk.Progressbar(info_win, orient="horizontal",  mode="determinate")
        progressbar.grid(row = 0, column = 2)
        progressbar["value"] = len(times)
        progressbar["maximum"] = len(names)

        cur = it_l[len(times)] if len(it_l)>len(times) else it_l[len(it_l)-1]
        it_l.reverse()
        analyze_format()
        if(len(times) != len(it_l)):
            for u in range (len(times)+1):
                tmp = it_l.pop()

            Button(info_win, text='Продолжить изучение' if len(times) != 0 else 'Начать изучение', command=lambda: golearn(var,studak,it_l,cur)).grid( row = 1, column = 2)
        else:
            Label(info_win, text="Вы закончили изучение курса").grid( row = 1, column = 2)

        Button(info_win, text='Назад', command=back).grid(row = 2, column = 2)

    def list_of_courses_student(studak):
        def back():
            list_win.destroy()
            win.update()
            win.deiconify()
        def goto(var,num):
            list_win.destroy()
            info(var,num)


        cursor.execute('''SELECT list_courses FROM Usr WHERE №_stud=?''', (studak,))
        lc = cursor.fetchall()

        list_courses = lc[0][0]
        lst = list_courses.split()
        l = []

        for course in lst:
            cursor.execute('''SELECT name FROM list_of_courses WHERE id=?''', (course,))
            tmp = cursor.fetchall()
            l.append(tmp[0][0])
        win.withdraw()
        list_win = Toplevel()
        list_win.title("просмотр курсов студента")
        list_win.geometry("300x150")

        variable = StringVar(list_win)
        variable.set(l[0])

        w = OptionMenu(list_win,variable, *l).place(relx=.3, rely=.15)
        var = variable.get()
        Button(list_win, text='Информация по выбранному курсу', command=lambda : goto(variable.get(),studak)) .place(relx=.15, rely=.45)

        Button(list_win, text='Назад', command = back).place(relx=.4, rely=.75)

    win = Toplevel()
    win.title("Главное окно студента")
    win.geometry("300x150")
    cursor.execute('''SELECT fio FROM Usr WHERE login=?''', (login,))
    name_of_student = cursor.fetchall()

    mess = "Добро пожаловать, " + name_of_student[0][0]
    Label(win, text=mess).pack()

    cursor.execute('''SELECT №_stud FROM Usr WHERE login=?''', (login,))
    stud = cursor.fetchall()
    Button(win, text='Просмотр курсов', command=lambda : list_of_courses_student(stud[0][0])).place(relx=.35, rely=.35)

    Button(win, text='Выйти', command=ex).place(relx=.35, rely=.75)



root = Tk()
root.title("Окно авторизации")
root.geometry("300x250")

label1 = Label(text="Логин")
label1.place(relx=.5,rely=.15, anchor="c")

message = StringVar()
message_entry = Entry(textvariable=message)
message_entry.place(relx=.5,rely=.25, anchor="c")

label2 = Label(text="Пароль")
label2.place(relx=.5,rely=.35, anchor="c")

message2 = StringVar()
message_entry2 = Entry(textvariable=message2,show="*")
message_entry2.place(relx=.5,rely=.45, anchor="c")
sql_file = 'C:\\Users\\Михаил\\PycharmProjects\\diploproj\\venv\\main.db'

db = sqlite3.connect(sql_file)
cursor = db.cursor()
cursor.execute('''SELECT * FROM Usr ''')
test = cursor.fetchall()

btn = Button(text="Вход", padx="6", pady="4", font="16", command=check)
btn.place(relx=.5, rely=.75, anchor="c")


root.mainloop()
