import psycopg2

class Queries:
	def __init__(self):
		self.__grades =  {'A':4, 'A-':3.7, 'B+':3.3, 'B':3, 'B-':2.7, \
			'C+':2.3, 'C':2, 'C-':1.7, 'D+':1.3, 'D':1, 'D-':0.7, 'F':0}

		self.__conn = psycopg2.connect(host="localhost", port=5432, \
    		dbname="small_example", user="gaespi")

		self.__cur = self.__conn.cursor()

		self.input = -1

	#recieve user input and return the that input
	def menu_selection(self):
		return input("Please Select a Number: \n" \
	        "0 - Exit\n" \
	        "1 - Generate Advisor List \n" \
	        "2 - Hire New Instructor \n" \
	        "3 - Generate Transcript \n" \
	        "4 - Generate Course List \n" \
	        "5 - Register Student for Course\n" \
	        "Input: ")

	#return a string that contains the advisor query
	def advisor_list(self):
		output = ''
		query = "select A.s_id, S.name as s_name, I.name as i_name from advisor as A " \
	            "join (" \
	            "select id, name from student) " \
	            "as S " \
	            "on A.s_id=S.id " \
	            "join (" \
	            "select id, name from instructor) " \
	            "as I " \
	            "on A.i_id=I.id;"
		self.__cur.execute(query)
		output += "Advisor List!\n"
		print("Advisor List!")
		colnames = [desc[0] for desc in self.__cur.description]
		print(colnames)
		output += "colnames\n"
		for advice in self.__cur:
			output += '{}|{}|{}\n'.format(advice[0].ljust(6), advice[1].ljust(10), advice[2].ljust(10))
			print('{}|{}|{}'.format(advice[0].ljust(6), advice[1].ljust(10), advice[2].ljust(10)))
		return output

	def hire(self):
		output = ""
		"""
	    primary - id in instructor must be unique
	    foreign - dept_name must exist department

	    if id is unique and dept_name in departments:
	        insert id, name, dept_name salary into instructor
	    """    
		new_id = input("ID of New Instructor: ") #int
		if not new_id.isnumeric():
			print("ERROR - ID value not numeric")
			return output
		q1 = "select * from instructor where id = %s;"
		self.__cur.execute(q1, (new_id,))
		if self.__cur.rowcount > 0:
		    print("ERROR - Not a unique ID value")
		    return output

		new_name = input("Name of New Instructor: ")
		if not new_name.isalpha():
		    print("ERROR - Name is not alphabetical")
		    return output

		new_dept_name = input("Department of New Instructor: ")
		q2 = "select * from department where dept_name = %s;"
		self.__cur.execute(q2, (new_dept_name,))
		if self.__cur.rowcount == 0:
		    print("ERROR - Department does not exist")
		    return output

		new_salary = input("Salary of New Instructor: ") #int
		if not new_salary.isnumeric():
		    print("ERROR - Salary value not numeric")
		    return output

		insert_query = "insert into instructor values (%s, %s, %s, %s);"
		try:
		    self.__cur.execute(insert_query, (new_id, new_name, new_dept_name, new_salary,))
		    self.__conn.commit()
		except Exception as e:
		    print(e)
		output += "Hire New Instructor!"
		print("Hire New Instructor!")
		return output

	def transcript(self):
		output = ""
		s_id = input("Enter Student ID: ")
		if not s_id.isnumeric():
		    print("ERROR - ID value not numeric")
		    return output
		q1 = "select * from student where id = %s;"
		self.__cur.execute(q1, (s_id,))
		if self.__cur.rowcount == 0:
		    print("ERROR - Student does not exist")
		    return output
		#transcript query
		tq = "select * from " \
		    "(select T.semester, T.year, T.grade, T.id, T.course_id, T.sec_id, " \
		    "S.name, S.dept_name, C.credits, C.title from student as S " \
		    "join takes as T on S.id=T.id join course as C on T.course_id=C.course_id)" \
		    " as Q where Q.id=%s order by Q.year, Q.semester desc;"

		try:
		    self.__cur.execute(tq, (s_id,))
		except Exception as e:
		    print(e)
		    return

		credits_tot = 0
		quality = 0

		cur_sem = None
		i = 0
		sem_gpa = 0
		total = 0 
		# print(f"Student ID: {cur[0][3]}")
		# print(f"{cur[0][6]}, {cur[0][7]}")
		sem = ''
		classes = []

		for row in self.__cur:
			if i == 0:
				output += f"\nStudent ID: {row[3]}\n"
				output += f"{row[6]}, {row[7]}\n"
				print(f"\nStudent ID: {row[3]}")
				print(f"{row[6]}, {row[7]}")
			if row[0] != cur_sem:
				if i != 0:
					output += f"\n{sem} {round(sem_gpa/total,2)}\n\n"
					print(f"\n{sem} {round(sem_gpa/total,2)}\n")
					for c in classes:
						output += f"   {c}\n"
						print("  ",c)
			output += f"{row[0]} {row[1]}\n"
			sem = f"{row[0]} {row[1]}"
			cur_sem = row[0]
			sem_gpa = 0
			total = 0
			classes = []
			classes.append(f"{row[4]}-{row[5]} {row[9]} ({row[8]}) {row[2]}")
			i+=1
			sem_gpa += (grades[row[2]] * float(row[8]))
			total += (float(row[8]))
			quality += (grades[row[2]] * float(row[8]))
			credits_tot += (float(row[8]))
		output += f"\n{sem} {round(sem_gpa/total,2)}\n\n"
		print(f"\n{sem} {round(sem_gpa/total,2)}\n")
		for c in classes:
			output += f"    {c}\n"
			print("  ",c)
		output += f"\nCumulative GPA {round(quality/credits_tot,2)}\n\n"
		output += "Generate Transcript!"
		print(f"\nCumulative GPA {round(quality/credits_tot,2)}\n")
		print("Generate Transcript!")
		return output

	def course_list():
		output = ""


		output += "Generate Course List!"
		print("Generate Course List!")
		return output

	def register():
		output = ""

		output += "Register A Student!"
		print("Register A Student!")
		return output


	def __exec(query, inp, commit=0):
		try:
			self.__cur(query, inp)
		except Exception as e:
			print(e)
q = Queries()

while q.input != 0:
	q.menu_selection()
	if q.input == "0":
		break
	elif q.input == "1":
	    q.advisor_list()
	elif q.input == "2":
	    q.hire()
	elif q.input == "3":
	    q.transcript()
	elif q.input == "4":
	    q.course_list()
	elif q.input == "5":
	    q.register()
	else:
	    print("Bad Input!")

# grades = {'A':4, 'A-':3.7, 'B+':3.3, 'B':3, 'B-':2.7, 'C+':2.3, 'C':2, 'C-':1.7, 'D+':1.3, 'D':1, 'D-':0.7, 'F':0}
# conn = psycopg2.connect(host="localhost", port=5432, \
#     dbname="small_example", user="gaespi")
# cur = conn.cursor()

# def menu_selection():
#     return input("Please Select a Number: \n" \
#         "0 - Exit\n" \
#         "1 - Generate Advisor List \n" \
#         "2 - Hire New Instructor \n" \
#         "3 - Generate Transcript \n" \
#         "4 - Generate Course List \n" \
#         "5 - Register Student for Course\n" \
#         "Input: ")
# def advisor_list():
#     query = "select A.s_id, S.name as s_name, I.name as i_name from advisor as A " \
#             "join (" \
#             "select id, name from student) " \
#             "as S " \
#             "on A.s_id=S.id " \
#             "join (" \
#             "select id, name from instructor) " \
#             "as I " \
#             "on A.i_id=I.id;"

#     cur.execute(query)
#     print("Advisor List!")
#     colnames = [desc[0] for desc in cur.description]
#     print(colnames)
#     for advice in cur:
#         print('{}|{}|{}'.format(advice[0].ljust(6), advice[1].ljust(10), advice[2].ljust(10)))
    

# def hire():
#     """
#     primary - id in instructor must be unique
#     foreign - dept_name must exist department

#     if id is unique and dept_name in departments:
#         insert id, name, dept_name salary into instructor
#     """    

#     new_id = input("ID of New Instructor: ") #int
#     if not new_id.isnumeric():
#         print("ERROR - ID value not numeric")
#         return
#     q1 = "select * from instructor where id = %s;"
#     cur.execute(q1, (new_id,))
#     if cur.rowcount > 0:
#         print("ERROR - Not a unique ID value")
#         return

#     new_name = input("Name of New Instructor: ")
#     if not new_name.isalpha():
#         print("ERROR - Name is not alphabetical")
#         return

#     new_dept_name = input("Department of New Instructor: ")
#     q2 = "select * from department where dept_name = %s;"
#     cur.execute(q2, (new_dept_name,))
#     if cur.rowcount == 0:
#         print("ERROR - Department does not exist")
#         return

#     new_salary = input("Salary of New Instructor: ") #int
#     if not new_salary.isnumeric():
#         print("ERROR - Salary value not numeric")
#         return

#     insert_query = "insert into instructor values (%s, %s, %s, %s);"
#     try:
#         cur.execute(insert_query, (new_id, new_name, new_dept_name, new_salary,))
#         conn.commit()
#     except Exception as e:
#         print(e)
#     print("Hire New Instructor!")

# def transcript():
#     s_id = input("Enter Student ID: ")
#     if not s_id.isnumeric():
#         print("ERROR - ID value not numeric")
#         return
#     q1 = "select * from student where id = %s;"
#     cur.execute(q1, (s_id,))
#     if cur.rowcount == 0:
#         print("ERROR - Student does not exist")
#         return
#     #transcript query
#     tq = "select * from " \
#         "(select T.semester, T.year, T.grade, T.id, T.course_id, T.sec_id, " \
#         "S.name, S.dept_name, C.credits, C.title from student as S " \
#         "join takes as T on S.id=T.id join course as C on T.course_id=C.course_id)" \
#         " as Q where Q.id=%s order by Q.year, Q.semester desc;"

#     try:
#         cur.execute(tq, (s_id,))
#     except Exception as e:
#         print(e)
#         return

#     credits_tot = 0
#     quality = 0

#     cur_sem = None
#     i = 0
#     sem_gpa = 0
#     total = 0 
#     # print(f"Student ID: {cur[0][3]}")
#     # print(f"{cur[0][6]}, {cur[0][7]}")
#     sem = ''
#     classes = []

#     for row in cur:
#         if i == 0:
#             print(f"\nStudent ID: {row[3]}")
#             print(f"{row[6]}, {row[7]}")
#         if row[0] != cur_sem:
#             if i != 0:
#                 print(f"\n{sem} {round(sem_gpa/total,2)}\n")
#                 for c in classes:
#                     print("  ",c)
#             sem = f"{row[0]} {row[1]}"
#             cur_sem = row[0]
#             sem_gpa = 0
#             total = 0
#             classes = []
#         classes.append(f"{row[4]}-{row[5]} {row[9]} ({row[8]}) {row[2]}")
#         i+=1
#         sem_gpa += (grades[row[2]] * float(row[8]))
#         total += (float(row[8]))
#         quality += (grades[row[2]] * float(row[8]))
#         credits_tot += (float(row[8]))
#     print(f"\n{sem} {round(sem_gpa/total,2)}\n")
#     for c in classes:
#         print("  ",c)

#     print(f"\nCumulative GPA {round(quality/credits_tot,2)}\n")
#     print("Generate Transcript!")

# def course_list():
#     print("Generate Course List!")

# def register():
#     print("Register A Student!")

# inp = -1
# while inp != "0":
#     inp = menu_selection()
#     if inp == "0":
#         break
#     elif inp == "1":
#         advisor_list()
#     elif inp == "2":
#         hire()
#     elif inp == "3":
#         transcript()
#     elif inp == "4":
#         course_list()
#     elif inp == "5":
#         register()
#     else:
#         print("Bad Input!")


# query = "select * from instructor where name = %s;"

# try:
#     cur.execute(query, (fac,))
#     for instructor in cur:
#         print(instructor[0], instructor[1], instructor[2], instructor[3])
# except psycopg2.ProgrammingError:
#     print("No such instructor")
