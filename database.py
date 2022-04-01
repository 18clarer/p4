#-----------------------------------------------------------------------
# database.py
# Author: Ryan Clare and Mateo Godoy
#-----------------------------------------------------------------------

from sqlite3 import connect
from contextlib import closing
from sys import argv, stderr

_DATABASE_URL = 'file:reg.sqlite?mode=rw'

#-----------------------------------------------------------------------
# takes inserts, an array of class details, as input and returns
# a tuple of the specified sql_string and an array of the modified
# inserts called 'details'
def get_class_sql(inserts):
    # build the first part of the sql string
    sql_string = "SELECT classid, dept, coursenum, area, title "
    sql_string += "FROM classes, courses, crosslistings "
    sql_string += "WHERE classes.courseid = courses.courseid AND "
    sql_string += "classes.courseid = crosslistings.courseid "

    # add to sql string depending on arguments
    if inserts['dept'] != '':
        sql_string += "AND dept LIKE ? ESCAPE '\\' "
    if inserts['number'] != '':
        sql_string += "AND coursenum LIKE ? ESCAPE '\\' "
    if inserts['area'] != '':
        sql_string += "AND area LIKE ? ESCAPE '\\' "
    if inserts['title'] != '':
        sql_string += "AND title LIKE ? ESCAPE '\\' "

    # add the ordering piece of the sql string
    sql_string += "ORDER BY dept ASC, coursenum ASC, classid ASC"

    # fill details array with modified values from the input
    # inserts array
    details = []
    for key in inserts:
        val = inserts[key]
        if val == '':
            continue
        insert = ""
        for char in val:
            if char in ('_', '%'):
                insert += "\\" + char
            else:
                insert += char

        insert = '%' + insert + '%'
        details.append(insert)

    return sql_string, details

#-----------------------------------------------------------------------
# takes an array inserts which holds the user input class details
# as an argument and returns a list of the classes that match
# the user's requested details from the reg.sqlite database
def class_search(inserts):
    # use a try clause to initialize the database connection and
    # query the database
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute('BEGIN')

                # get the sql string and modified inserts
                # array as specified by the parameter inserts
                sql_string, inserts = get_class_sql(inserts)

                cursor.execute(sql_string, inserts)

                # fetch the first row
                row = cursor.fetchone()

                # loop through all the rows and store
                # class info
                classes = []
                while row is not None:
                    info = {}
                    info['classid'] = row[0]
                    info['dept'] = row[1]
                    info['coursenum'] = row[2]
                    info['area'] = row[3]
                    info['title'] = row[4]

                    classes.append(info)
                    row = cursor.fetchone()

                cursor.execute('COMMIT')

                return True, classes

    # catch and print any exceptions
    except Exception as ex:
        if str(ex) != "'NoneType' object is not subscriptable":
            print(argv[0] + ': ' + str(ex), file=stderr)

        return False, str(ex)

#-----------------------------------------------------------------------
# takes an integer classid as an argument and returns the details of
# the class with that id from the sqlite database
def details_query(classid):
    # use a try clause to initialize the database connection and
    # query the database
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute('BEGIN')

                # build sql string to query classes
                # and courses tables
                sql_string = \
                    "SELECT classes.courseid, days, starttime, "
                sql_string += \
                    "endtime, bldg, roomnum, area, title, "
                sql_string += \
                    "descrip, prereqs FROM classes, courses "
                sql_string += \
                    "WHERE classid = ? AND courses.courseid "
                sql_string += \
                    "= classes.courseid"

                cursor.execute(sql_string, [classid])
                row = cursor.fetchone()

                # store the query results
                classes = {}
                classes['courseid'] = row[0]
                classes['days'] = row[1]
                classes['starttime'] = row[2]
                classes['endtime'] = row[3]
                classes['bldg'] = row[4]
                classes['roomnum'] = row[5]
                classes['area'] = row[6]
                classes['title'] = row[7]
                classes['descrip'] = row[8]
                classes['prereqs'] = row[9]

                # build sql string to get the departments
                sql_string = "SELECT dept, coursenum FROM "
                sql_string += "crosslistings WHERE "
                sql_string += "crosslistings.courseid = ? "
                sql_string += "ORDER BY dept ASC, "
                sql_string += "coursenum ASC"

                cursor.execute(sql_string, [classes['courseid']])
                classes['dept_and_num'] = cursor.fetchall()

                # build sql string to get the professor names
                sql_string = "SELECT profname FROM profs, "
                sql_string += "coursesprofs WHERE "
                sql_string += "coursesprofs.courseid = ? "
                sql_string += "AND profs.profid = "
                sql_string += "coursesprofs.profid ORDER BY "
                sql_string += "profname ASC"

                cursor.execute(sql_string, [classes['courseid']])
                classes['profnames'] = cursor.fetchall()

                cursor.execute('COMMIT')

                return True, classes

    # catch and print any exceptions
    except Exception as ex:
        if str(ex) != "'NoneType' object is not subscriptable":
            print(argv[0] + ': ' + str(ex), file=stderr)

        return False, str(ex)
