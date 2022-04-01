#-----------------------------------------------------------------------
# flask_app.py
# Author: Ryan Clare and Mateo Godoy
#-----------------------------------------------------------------------
from urllib.parse import quote_plus
from flask import Flask, request, make_response
from flask import render_template
from database import class_search, details_query


#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------
# loads the searchform template
@app.route('/', methods=['GET'])
def index_controller():

    html = render_template('searchform.html', classes=[])
    response = make_response(html)

    return response

#-----------------------------------------------------------------------
# performs the AJAX query for classes based on user input
@app.route('/results', methods=['GET'])
def search_form():
    # intialize an inserts dictionary which holds the user input
    # class details
    inserts = {}

    # fill inserts dictionary
    dept = request.args.get('dept')
    if (dept is None) or (dept.strip() == ''):
        dept = ''
    inserts['dept'] = dept
    number = request.args.get('coursenum')
    if (number is None) or (number.strip() == ''):
        number = ''
    inserts['number'] = number
    area = request.args.get('area')
    if (area is None) or (area.strip() == ''):
        area = ''
    inserts['area'] = area
    title = request.args.get('title')
    if (title is None) or (title.strip() == ''):
        title = ''
    inserts['title'] = title

    # get the classes which match the inserts array from
    # database.py
    status, classes = class_search(inserts)

    if status is False:
        html = """<div class="container-fluid">
                    <p>A server error occurred. Please contact the 
                    system administrator.</p>
                 </div> """

        response = make_response(html)
        return response

    html = render_template('classes.html', classes=classes)
    response = make_response(html)

    return response

#-----------------------------------------------------------------------
# view controller for the regdetails page
@app.route('/regdetails', methods=['GET'])
def reg_details():
    classid = request.args.get('classid')

    # handle missing classid
    if classid is None or classid == '':
        html = render_template('error.html',
        error_message = 'missing classid')

        return make_response(html)

    # get previous search from cookie data
    dept = quote_plus(request.cookies.get('prev_dept'))
    number = quote_plus(request.cookies.get('prev_num'))
    area = quote_plus(request.cookies.get('prev_area'))
    title = quote_plus(request.cookies.get('prev_title'))

    # try to convert the class id to an integer
    # redirect to error page if unsuccessful
    try:
        classid = int(classid)
    except Exception:
        html = render_template('error.html',
        error_message = 'non-integer classid')

        return make_response(html)

    status, details = details_query(classid)

    # if there was a database error, show the error page
    if status is False:
        if details == "'NoneType' object is not subscriptable":
            error_message = 'no class with classid {} \
                exists'.format(classid)
        else:
            error_message = 'A server error occurred. \
            Please contact the system administrator. '

        html = render_template('error.html',
        error_message = error_message)

        return make_response(html)

    html = render_template('reg_details.html',
        classid=classid,
        details=details,
        dept=dept,
        number=number,
        area = area,
        title = title
        )
    response = make_response(html)

    return response
