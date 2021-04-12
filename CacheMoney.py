import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, \
    dbname="small_example", user="jwdeve")
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
    query = "select A.s_id, S.name, I.name from advisor as A " \
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
        print(advice[0], advice[1], advice[2])
    

def hire():
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
