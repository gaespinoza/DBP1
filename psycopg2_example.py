import psycopg2

def menu_selection():
    return input("Enter the name of a faculty member " \
        "to get information on that person: ")

conn = psycopg2.connect(host="localhost", port=5432, \
    dbname="small_example", user="jwdeve")
cur = conn.cursor()


fac = menu_selection()
query = "select * from instructor where name = %s;"

try:
    cur.execute(query, (fac,))
    for instructor in cur:
        print(instructor[0], instructor[1], instructor[2], instructor[3])
except psycopg2.ProgrammingError:
    print("No such instructor")
