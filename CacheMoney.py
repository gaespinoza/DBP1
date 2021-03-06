import psycopg2

sems = {'spring':'Spring', 'summer':'Summer','fall':'Fall','winter':'Winter'}


class Queries:
	def __init__(self):
		self.__grades =  {'A':4, 'A-':3.7, 'B+':3.3, 'B':3, 'B-':2.7, \
			'C+':2.3, 'C':2, 'C-':1.7, 'D+':1.3, 'D':1, 'D-':0.7, 'F':0, None:100}

		self.__conn = psycopg2.connect(host="localhost", port=5432, \
    		dbname="small_example", user="gaespi")

		self.__cur = self.__conn.cursor()

		self.input = -1

	#recieve user input and return the that input
	def menu_selection(self):
		self.input = input("Please Select a Number: \n" \
	        "0 - Exit\n" \
	        "1 - Generate Advisor List \n" \
	        "2 - Hire New Instructor \n" \
	        "3 - Generate Transcript \n" \
	        "4 - Generate Course List \n" \
	        "5 - Register Student for Course\n" \
	        "Input: ")
		return self.input

	#return a string that contains the advisor query
	def advisor_list(self):
		output = ''
		query = "select A.s_id as Student_ID, S.name as Student, I.name as Instructor from advisor as A " \
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
		colnames = [desc[0] for desc in self.__cur.description]

		output += '{}|{}|{}\n'.format(colnames[0].center(15), colnames[1].center(15), colnames[2].center(15))
		for advice in self.__cur:
			output += '{}|{}|{}\n'.format(advice[0].center(15), advice[1].center(15), advice[2].center(15))
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

		new_name = input("Name of New Instructor: ")

		new_dept_name = input("Department of New Instructor: ")
		q2 = "select * from department where dept_name = %s;"

		new_salary = input("Salary of New Instructor: ") #int

		insert_query = "insert into instructor values (%s, %s, %s, %s);"

		#create exceptions for each variations of errors that may arise for different inputs
		try:
		    self.__cur.execute(insert_query, (new_id, new_name, new_dept_name, new_salary,))
		    self.__conn.commit()
		    output += "Hire Successful!"
		except psycopg2.errors.UniqueViolation:
			output = "ERROR - ID value not valid"
		except psycopg2.errors.ForeignKeyViolation:
			output = "ERROR - Department does not exist"
		except psycopg2.errors.CheckViolation:
			output = "ERROR - Salary value is too low"
		except psycopg2.errors.SyntaxError:
			output = "ERROR - letters placed in salary field"
		except Exception as e:
			output = str(e)
		return output

	def transcript(self):
		output = ""
		s_id = input("Enter Student ID: ")

		q1 = "select * from student where id = %s;"
		self.__cur.execute(q1, (s_id,))
		if self.__cur.rowcount == 0:
		    output = "ERROR - Student does not exist"
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
		    output = str(e)
		    return output

		#------------------------- output the table that has been returned properly -------------------------------

		credits_tot = 0
		quality = 0

		cur_sem = None
		i = 0
		sem_gpa = 0
		total = 0 
		sem = ''
		classes = []
		#iterate through each semester to update the Cumulative GPA and Semester GPA
		for row in self.__cur:
			#only add on the first iteration for proper formatting for student information
			if i == 0:
				output += f"\nStudent ID: {row[3]}\n"
				output += f"{row[6]}, {row[7]}\n"
			#If the row does not match the current semester we have a new semester and should
			#prepare the formatting to take into account a new section
			if row[0] != cur_sem:
				if i != 0:
					if total != 0:
						output += f"\n{sem} {round(sem_gpa/total,2)}\n\n"
					else:
						output += f"\n{sem} {round(0.00,2)}\n\n"
					for c in classes:
						output += f"   {c}\n"
				sem = f"{row[0]} {row[1]}"
				cur_sem = row[0]
				sem_gpa = 0
				total = 0
				classes = []
			#add each course to the list of classes the student has taken in the current semester
			classes.append(f"{row[4]}-{row[5]} {row[9]} ({row[8]}) {row[2]}")
			i+=1
			#If the student has a grade for the course, take it into account for calculation of the GPA
			if self.__grades[row[2]] != 100:
				sem_gpa += (self.__grades[row[2]] * float(row[8]))
				total += (float(row[8]))
				quality += (self.__grades[row[2]] * float(row[8]))
				credits_tot += (float(row[8]))
		#this is for a special case when the student has not completed a course for the current semester
		if total != 0:
			output += f"\n{sem} {round(sem_gpa/total,2)}\n\n"
		else:
			output += f"\n{sem} {round(0.00,2)}\n\n"
		for c in classes:
			output += f"    {c}\n"
		output += f"\nCumulative GPA {round(quality/credits_tot,2)}\n\n"
		return output

	def course_list(self):
		output = ""
		semester = input("What semester will you like to look at? \ninput: ")

		year = input("What year will you like to look at? \ninput: ")


		query = "select * from (select C.course_id, C.title, C.credits, S.sec_id, S.semester, S.year, S.building, S.room_number, CL.capacity, TA.enrollment, S.time_slot_id "\
		    "from course as C " \
		    "join section as S on C.course_id = S.course_id "\
		    "join classroom as CL on S.building = CL.building and S.room_number = CL.room_number "\
		    "join ( select T.course_id, T.sec_id, T.semester, T.year, count(*) as enrollment from takes as T "\
		    "group by T.course_id, T.sec_id, T.semester, T.year) as TA on S.course_id = TA.course_id and S.sec_id = TA.sec_id and S.semester = TA.semester and S.year = TA.year) as Table1 "\
		    "where Table1.semester=%s and Table1.year=%s;"
		try:
			self.__cur.execute(query, (semester, year,))

			for row in self.__cur:
				formating = f"\n{row[0]}-{row[3]} {row[1]} ({row[2]}) {row[6]} {row[7]} {row[8]} {row[9]}"

				#sub query to get the time slot information more easily for formatting

				temp_conn = self.__conn.cursor()

				sub_q = "select * from time_slot where time_slot_id=%s;"

				temp_conn.execute(sub_q,(row[10],))
				for day in temp_conn:
					formating += f"\n {day[1]} {day[2]}:{int(day[3]):02d}-{day[4]}:{day[5]}"
				output += formating
		except psycopg2.errors.InvalidTextRepresentation:
			output = "ERROR: Please input a number for year"
		return output

	def register(self):
		"""
	    1 - check if student id is valid (table: student)
	    2 - check if course is valid with given semester, year, course id and section id (table: section)
	    3 - check if course has space (query from 4)
	    4 - check that student has not taken course (table: takes)
	    5 - check if course has prerequistes (table: prereq)
	    6 - check if student has all prerequistes (table: prereq -> table: takes)
	    7 - check if student has no conflicting courses (takes with id=s_id->section check time_slot_id=/=c_id)
	    8 - register student for course in takes table(insert into takes)
    	"""

		output = ""
		s_id = input("Student ID: ")
		s_query = 'Select * from student where id=%s;'

		self.__cur.execute(s_query, (s_id,))
		if self.__cur.rowcount == 0:
			output = 'Error - Invalid Student ID'
			return output 

	    #checking valid course
		semester = input("Semester of Course: ")
		year = input("Year of registration: ")
		c_id = input("Course ID: ")
		sec_id = input("Section ID: ")

		c_query = 'Select * from section where course_id=%s and sec_id=%s and semester=%s and year=%s;'
		try:
			self.__cur.execute(c_query, (c_id, sec_id, semester, year,))
			if self.__cur.rowcount == 0:
				output = 'Invalid Course Information'
				return output 
			for i in self.__cur:
				time_slot = i[6]
		except Exception as e:
			output = f"Error: Invalid input for year"
			return output

	    #Checking course capacity
		cap_query = "select capacity, enrollment from (select C.course_id, C.title, C.credits, S.sec_id, S.semester, S.year, S.building, S.room_number, CL.capacity, TA.enrollment, S.time_slot_id "\
			"from course as C " \
			"join section as S on C.course_id = S.course_id "\
			"join classroom as CL on S.building = CL.building and S.room_number = CL.room_number "\
			"join ( select T.course_id, T.sec_id, T.semester, T.year, count(*) as enrollment from takes as T "\
			"group by T.course_id, T.sec_id, T.semester, T.year) as TA on S.course_id = TA.course_id and S.sec_id = TA.sec_id and S.semester = TA.semester and S.year = TA.year) as Table1 "\
			"where Table1.course_id = %s and Table1.sec_id=%s and Table1.semester=%s and Table1.year=%s;"


		self.__cur.execute(cap_query, (c_id, sec_id, semester, year,))
		for i in self.__cur:
			if i[0] < i[1]:
				output = "No seats available"
				return output 

		#Checking if class has been taken already
		taken_query = 'select * from takes where ID=%s and course_id=%s;'

		self.__cur.execute(taken_query, (s_id, c_id,))
		if self.__cur.rowcount != 0:
			output = "Student has already taken course"
			return output 

	    #check if course has prereqs, If so, check if student has taken courses
		check_query = 'select * from prereq where course_id=%s;'
		pr_query = 'select * from takes where ID=%s and course_id=%s;'

		self.__cur.execute(check_query, (c_id,))
		if self.__cur.rowcount != 0:
			temp_conn = self.__conn.cursor()
			for i in self.__cur:
				temp_conn.execute(pr_query, (s_id, i[1],))
				if temp_conn.rowcount == 0:
					output = 'Student has not fulfilled prerequiste requirements' 
					return output 


		#Check if conflicting time slots
		check_query = 'select * from takes where ID=%s;'
		# time_query = 'select * from section where semester=%s and year=%s and time_slot_id=%s;'
		time_query = 'select * from section where course_id = %s;'

		self.__cur.execute(check_query, (s_id,))
		temp_conn = self.__conn.cursor()
		if self.__cur.rowcount > 0:
			for i in self.__cur:
				temp_conn.execute(time_query, (i[1],))
				for j in temp_conn:
					if j[1] == semester and j[3] == year and j[6] == time_slot:
						output = "Conflicting Registration Error"
						return output 

	    #enter student registration into takes table
		insert_statement = "insert into takes values(%s, %s, %s, %s, %s);"
		try:
			self.__cur.execute(insert_statement, (s_id, c_id, sec_id, semester, year,))
			self.__conn.commit()
		except Exception as e:
			output = f"Error: {e}"
			return output 

		output += "Registration Successful!"
		return output

q = Queries()

while q.input != 0:
	q.menu_selection()
	if q.input == "0":
		break
	elif q.input == "1":
	    print(q.advisor_list())
	elif q.input == "2":
	    print(q.hire())
	elif q.input == "3":
	    print(q.transcript())
	elif q.input == "4":
	    print(q.course_list())
	elif q.input == "5":
	    print(q.register())
	else:
	    print("Bad Input!")

