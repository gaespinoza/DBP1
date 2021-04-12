import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, \
    dbname="small_example", user="gaespi")
cur = conn.cursor()

def menu_selection():
    return input("Please Select a Number: \n" \
        "0 - Exit\n" \
        "1 - Generate Advisor List \n" \
        "2 - Hire New Instructor \n" \
        "3 - Generate Transcript \n" \
        "4 - Generate Course List \n" \
        "5 - Register Student for Course\n" \
        "Input: ")
def advisor_list():
    query = "select A.s_id, S.name as s_name, I.name as i_name from advisor as A " \
            "join (" \
            "select id, name from student) " \
            "as S " \
            "on A.s_id=S.id " \
            "join (" \
            "select id, name from instructor) " \
            "as I " \
            "on A.i_id=I.id;"

    cur.execute(query)
    print("Advisor List!")
    colnames = [desc[0] for desc in cur.description]
    print(colnames)
    for advice in cur:
        print('{}|{}|{}'.format(advice[0].ljust(6), advice[1].ljust(10), advice[2].ljust(10)))
    

def hire():
    """
    primary - id in instructor must be unique
    foreign - dept_name must exist department

    if id is unique and dept_name in departments:
        insert id, name, dept_name salary into instructor
    """    

    new_id = input("ID of New Instructor: ") #int
    if not new_id.isnumeric():
        print("ERROR - ID value not numeric")
        return
    q1 = "select * from instructor where id = %s;"
    cur.execute(q1, (new_id,))
    if cur.rowcount > 0:
        print("ERROR - Not a unique ID value")
        return

    new_name = input("Name of New Instructor: ")
    if not new_name.isalpha():
        print("ERROR - Name is not alphabetical")
        return

    new_dept_name = input("Department of New Instructor: ")
    q2 = "select * from department where dept_name = %s;"
    cur.execute(q2, (new_dept_name,))
    if cur.rowcount == 0:
        print("ERROR - Department does not exist")
        return

    new_salary = input("Salary of New Instructor: ") #int
    if not new_salary.isnumeric():
        print("ERROR - Salary value not numeric")
        return

    insert_query = "insert into instructor values (%s, %s, %s, %s);"
    try:
        cur.execute(insert_query, (new_id, new_name, new_dept_name, new_salary,))
        check = "select * from instructor;"
        cur.execute(check)
        conn.commit()
        for row in cur:
            print(row[0], row[1], row[2], row[3])
    except Exception as e:
        print(e)
    print("Hire New Instructor!")

def transcript():
    print("Generate Transcript!")

def course_list():
    print("Generate Course List!")

def register():
    print("Register A Student!")

inp = -1
while inp != "0":
    inp = menu_selection()
    if inp == "0":
        break
    elif inp == "1":
        advisor_list()
    elif inp == "2":
        hire()
    elif inp == "3":
        transcript()
    elif inp == "4":
        course_list()
    elif inp == "5":
        register()
    else:
        print("Bad Input!")


# query = "select * from instructor where name = %s;"

# try:
#     cur.execute(query, (fac,))
#     for instructor in cur:
#         print(instructor[0], instructor[1], instructor[2], instructor[3])
# except psycopg2.ProgrammingError:
#     print("No such instructor")
