#######################################################################################################################################################
# Description : 
#     This program will process two functions :
#         1. An Get financial_data API to retrieve records from financial_data table.
#         2. An Get statistics API to perform the following calculations on the data in given period of time.
#             2.1. Calculate the average daily open price for the period.
#             2.2. Calculate the average daily closing price for the period.
#             2.3. Calculate the average daily volume for the period. 
#
# Remark : 
#     None 
#######################################################################################################################################################


# Flask application
import flask
from flask import jsonify, request
# Date time format
import datetime
# SQL function
import sqlite3 as sql
from sqlite3 import Error


# Create flask app and set configuration
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False
# Create error message list as a global variable
error_list = []


# This functoin is used to connect to a database
# input : db_file - database file name
# output : con - db connect point
def db_connection(db_file):
    # Use global error message list
    global error_list
    con = None
    try:
        con = sql.connect(db_file)
    except Error as e:
        error_list.append(e)
    return con

    
# This functoin is used to check the date format
# input : date - date value to be checked the format
# output : True  - date format is right, it is a date string
#          False - date format is wrong, it is not a date string
def validate_date(date):
    try:
        datetime.date.fromisoformat(date)
        return True
    except ValueError:
        return False


# This functoin is used to check the date string
# input : date    - date value to be checked the format
#         message - error message to be stored to the global error list 
# output : date - date value, it is a date string
#          None - force to None, it is not a date string        
def check_date(date, message):
    # Use global error message list
    global error_list
    if validate_date(date):
        return date
    else:
        error_list.append('Parameter [%s] input the wrong format or value [%s]' % (message, date))
        return None


# This functoin is used to check the symbol string is in the symbol list
# input : symbol - symbol value to be checked the format
# output : symbol - symbol value, it is a symbol string
#          None   - force to None, it is not a symbol string
def check_symbol(symbol):
    # Use global error message list
    global error_list
    if symbol == 'IBM' or symbol == 'Apple Inc.':
        return symbol
    else:
        error_list.append('Parameter [symbol] input the wrong format or value [%s], avaiable symbol is \'IBM\' or \'Apple Inc.\'' % (symbol))
        return None


# This functoin is used to check the integer string
# input : value      - value to be checked the format
#         message    - error message to be stored to the global error list
#         init_value - initial value to output if the input value is not a integer
# output : value      - value as integer, it is a integer string
#          init_value - given initial value, it is not a integer string
def check_integer(value, message, init_value):
    # Use global error message list
    global error_list
    if value.isdigit() and int(value) > 0:
        # Transfer the type from string to integer
        return int(value)
    else:
        error_list.append('Parameter [%s] input the wrong format or value [%s]' % (message, value))
        return init_value


# This functoin is used to query the data from database
# input : condition - condition filter to be used for query command
# output : results - database query result
def select_table(condition):
    # Use global error message list
    global error_list
    results = []
    database = "financial_data.db"
    # Create a database connection
    connection = db_connection(database)
    with connection:
        # Create a database cursor
        cursor = connection.cursor()
        if condition:
            # Query with condition
            sql_cmd = ''' SELECT * FROM financial_data WHERE %s ORDER BY symbol ASC, date ASC ''' % (condition)
        else:
            # Query without condition
            sql_cmd = ''' SELECT * FROM financial_data ORDER BY symbol ASC, date ASC '''
        cursor.execute(sql_cmd)
        # Get the query data
        results = cursor.fetchall()
        # Close database cursor
        cursor.close()
    # Close database connection
    connection.close()
    return results


# This functoin is used to build the condition string for query
# input : old_condition    - current condition string
#         append_condition - new condition string to be appended 
# output : old_condition + 'and ' + append_condition - combine the current condition string with appended condition string
#          append_condition                          - appended condition string, current condition string is null 
def build_sqlite_condition(old_condition, append_condition):
    if old_condition:
        # Add 'and' between two condition string
        return old_condition + 'and ' + append_condition
    else:  
        return append_condition
        

# This functoin is used to run as home page
# output : usage of this program
@app.route('/', methods=['GET'])
def home():
    usage_string = '                              This API support two functions for using :\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '                    1. /api/financial_data : an Get financial_data API to retrieve records from financial_data table\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '                API Parameters :\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Optional : start_date\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The first date condition for query database. Format should be YYYY-MM-DD. For example: 2023-04-20.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Optional : end_date\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The last date condition for query database. Format should be YYYY-MM-DD. For example: 2023-04-20.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Optional : symbol\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The symbol condition for query database. The following values are supported: "IBM", "Apple Inc.".\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Optional : limit\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The data count displayed in one page. The value should large than 1.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Optional : page\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The current data page to display. The value should large than 1.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '                Example :\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            http://localhost:5000/api/financial_data?start_date=2023-01-01&end_date=2023-01-14&symbol=IBM&limit=3&page=2\n'    
    usage_string = usage_string + '<br />' + '&emsp;' + '                    2. /api/statistics : an Get statistics API to perform the calculations on the data in given period of time\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '                API Parameters :\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Required : start_date\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The first date condition for query database. Format should be YYYY-MM-DD. For example: 2023-04-20.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Required : end_date\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The last date condition for query database. Format should be YYYY-MM-DD. For example: 2023-04-20.\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            Required : symbol\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '&emsp;' + '                The symbol condition for query database. The following values are supported: "IBM", "Apple Inc.".\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '                Example :\n'
    usage_string = usage_string + '<br />' + '&emsp;' + '&emsp;' + '&emsp;' + '            http://localhost:5000/api/statistics?start_date=2023-01-01&end_date=2023-01-31&symbol=IBM\n'
    return usage_string


# This functoin is used to run for api /api/financial_data
# output : result with three properties:
#              data: an array includes actual results
#              pagination: handle pagination with four properties
#                  count: count of all records without panigation
#                  page: current page index
#                  limit: limit of records can be retrieved for single page
#                  pages: total number of pages
#              info: includes any error info if applies
@app.route('/api/financial_data', methods=['GET'])
def financial_data():
    # Use global error message list
    global error_list
    # Assign the initial value to variables
    error_list = []
    data_List = []
    pagination_dict = {}
    info_dict = {}
    output_dict = {}
    sql_results = []
    sql_condition = None
    # Check the date format of input parameter start_date, give default value None if format is wrong
    if 'start_date' in request.args:
        start_date = check_date(request.args['start_date'], 'start_date')
    else:
        start_date = None
    # Check the date format of input parameter end_date, give default value None if format is wrong
    if 'end_date' in request.args:
        end_date = check_date(request.args['end_date'], 'end_date')
    else:
        end_date = None
    # Check the string format of input parameter symbol, give default value None if format is wrong        
    if 'symbol' in request.args:
        symbol = check_symbol(request.args['symbol'])
    else:
        symbol = None
    # Check the integer format of input parameter limit, give default value 5 if format is wrong
    if 'limit' in request.args:
        limit = check_integer(request.args['limit'], 'limit', 5)
    else:
        limit = 5
    # Check the integer format of input parameter page, give default value 1 if format is wrong
    if 'page' in request.args:
        page = check_integer(request.args['page'], 'page', 1)
    else:
        page = 1
    # Build the database query condition
    if start_date and end_date:
        # Both start_date and end_date is given, check if the input value is opposite
        if start_date > end_date:
            sql_condition = build_sqlite_condition(sql_condition, 'date >= "%s" and date <= "%s" ' % (end_date, start_date))
        else:
            sql_condition = build_sqlite_condition(sql_condition, 'date >= "%s" and date <= "%s" ' % (start_date, end_date))
    else:
        # Check if one of the start_date or end_date is given
        if start_date:
            sql_condition = build_sqlite_condition(sql_condition, 'date >= "%s" ' % (start_date))
        if end_date:
            sql_condition = build_sqlite_condition(sql_condition, 'date <= "%s" ' % (end_date))
    # Check if symbol is given, add into query condition
    if symbol:
        sql_condition = build_sqlite_condition(sql_condition, 'symbol = "%s" ' % (symbol))
    # Query database
    sql_results = select_table(sql_condition)
    # Get the result count of data
    count = len(sql_results)
    # Error handle when count is 0
    if count < 1:
        pages = 1
        page = 1
        error_list.append('Data not found in database')    
    else:
        # Get the total pages number
        pages = int(count / limit)
        if (count % limit) > 0:
            pages += 1
        # Check if the input page is over the size of total pages number, assign the max size to page
        if page > pages:
            page = pages
            error_list.append('Given parameter [page] is over than current data size, force page as the maximum number of pages')
        # Get the index of data to display in current page 
        current_index = (page - 1) * limit
        max_index = current_index + limit
        # Check if the page is the max page and the data is not enough to display in one page
        if max_index > count:
            max_index = count
        # Build the data list 
        for i in range(current_index, max_index, 1):
            data_dict = {'symbol': '%s' % sql_results[i][0], 'date': '%s' % sql_results[i][1], 'open_price': '%s' % sql_results[i][2], 'close_price': '%s' % sql_results[i][3], 'volume': '%s' % sql_results[i][4]}
            data_List.append(data_dict)
    # Build the pagination dictionary            
    pagination_dict = {'count': count, 'page': page, 'limit': limit, 'pages': pages}
    # Build the info dictionary
    info_dict = {'error': error_list}
    # Build the output dictionary
    output_dict = {'data': data_List, 'pagination': pagination_dict, 'info': info_dict}
    return jsonify(output_dict)


# This functoin is used to run for api /api/statistics
# output : result with two properties:
#              data: calculated statistic results
#              info: includes any error info if applies
@app.route('/api/statistics', methods=['GET'])
def statistics():
    # Use global error message list
    global error_list
    # Assign the initial value to variables
    error_list = []
    info_dict = {}
    data_dict = {}
    output_dict = {}
    sql_results = []
    average_daily_open_price = 0
    average_daily_close_price = 0
    average_daily_volume = 0
    num_of_days = 0
    # Check the date format of input parameter start_date, give default value None if format is wrong   
    if 'start_date' in request.args:
        start_date = check_date(request.args['start_date'], 'start_date')
    else:
        start_date = None
        error_list.append('Parameter [start_date] must be provided')
    # Check the date format of input parameter end_date, give default value None if format is wrong
    if 'end_date' in request.args:
        end_date = check_date(request.args['end_date'], 'end_date')
    else:
        end_date = None
        error_list.append('Parameter [end_date] must be provided')
    # Check the string format of input parameter symbol, give default value None if format is wrong
    if 'symbol' in request.args:
        symbol = check_symbol(request.args['symbol'])
    else:
        symbol = None
        error_list.append('Parameter [symbol] must be provided')
    # Check if all the three parameters are given as correct value
    if start_date == None or end_date == None or symbol == None:
        error_list.append('All the parameters [start_date, end_date, symbol] must be provided with correct format before running this API')
        # Build the info dictionary
        info_dict = {'error': error_list}
        # Build the output dictionary
        output_dict = {'data': data_dict, 'info': info_dict}
        # Do nothing if one of the parameter is incorrect
        return jsonify(output_dict)
    # Check if the input value is opposite
    if start_date > end_date:
        big_date = start_date
        small_date = end_date
    else:
        big_date = end_date
        small_date = start_date
    # Query database
    sql_results = select_table('date >= "%s" AND date <= "%s" AND symbol = "%s"' % (small_date, big_date, symbol))
    # Add the value from each column of data
    for row in sql_results:
        average_daily_open_price += row[2]
        average_daily_close_price += row[3]
        average_daily_volume += int(row[4])
        num_of_days += 1
    # Check if the query result has data output
    if num_of_days < 1:
        # Force to 0 if no data is return from query database
        average_daily_open_price = ('%.2f' % 0)
        average_daily_close_price = ('%.2f' % 0)
        average_daily_volume = 0
        error_list.append('Data not found between [%s] ~ [%s]' % (small_date, big_date))
    else:
        # Calculate the average value
        average_daily_open_price = ('%.2f' % (average_daily_open_price / num_of_days))
        average_daily_close_price = ('%.2f' % (average_daily_close_price / num_of_days))
        average_daily_volume = int((average_daily_volume / num_of_days))
    # Build the data dictionary
    data_dict = {'start_date': small_date, 'end_date': big_date, 'symbol': symbol, 'average_daily_open_price': average_daily_open_price, 'average_daily_close_price': average_daily_close_price, 'average_daily_volume': average_daily_volume}
    # Build the info dictionary    
    info_dict = {'error': error_list}
    # Build the output dictionary
    output_dict = {'data': data_dict, 'info': info_dict}
    return jsonify(output_dict)


# Run the application
app.run(host='0.0.0.0')
