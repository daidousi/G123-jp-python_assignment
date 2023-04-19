#######################################################################################################################################################
# Description : 
#     This program will process below action :
#         1. Get API Key from encrypted key files.
#         2. Open local database, create the database if it doesn't exist.
#         3. Check table in database, create the table if it doesn't exist.
#         4. Do house keeping to delete the old data from table. 2 weeks is the limitation.
#         5. Get the financial data of two given stocks (IBM, Apple Inc.) by AlphaVantage free API.
#         6. Insert the most recently two weeks financial data to database. 
#
# Remark : 
#     Please call "python encryptAPIKEY.py" once to create the encrypted key files before the first time using this program.
#     This program can be put into the crontab to auto process everyday to update the data in database. 
#######################################################################################################################################################


# CSV data process
import pandas as pd
# Get data from url
import requests as rq
# Get today date
import datetime
# SQL function
import sqlite3 as sql
from sqlite3 import Error
# Decrypt the AlphaVantage API KEY
import decryptAPIKEY as decrypt
# File operation
import os


# This functoin is used to connect to a database
# input : db_file - database file name
# output : con - db connect point
def db_connection(db_file):
    con = None
    try:
        con = sql.connect(db_file)
    except Error as e:
        print(e)
    return con


# This functoin is used to check the table is existed in database
# input : cur - db cursor point
# output : result = 0 - table doesn't exist
#          result = 1 - table existes
def check_table(cur):
    sql_cmd = ''' SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='financial_data' '''
    cur.execute(sql_cmd)
    result = cur.fetchone()[0]
    return result


# This functoin is used to create the table in database
# input : con - db connect point
#         cur - db cursor point
def create_table(con, cur):
    # Read table schema from file
    with open('schema.sql', 'r') as fsql:
        sql_cmd = fsql.read()
        cur.execute(sql_cmd)
        con.commit()
     
     
# This functoin is used to delete the expired data from table by giving the expired date
# input : con  - db connect point
#         cur  - db cursor point
#         date - expired date
def house_keeping(con, cur, date):
    sql_cmd = ''' DELETE FROM financial_data WHERE date < "%s" ''' % (date)
    cur.execute(sql_cmd)
    con.commit()


# This functoin is used to insert the data to table
# input : con  - db connect point
#         cur  - db cursor point
#         data - data to be insert into table, the format is [data1, data2, data3, data4, data5], where data1, data2, data5 is str and data3, data4 is float
# output : result - the row id for this insert    
def insert_table(con, cur, data):
    sql_cmd = ''' INSERT INTO financial_data(symbol, date, open_price, close_price, volume) VALUES(?,?,?,?,?) '''
    cur.execute(sql_cmd, data)
    result = cur.lastrowid
    con.commit()
    return result


# This functoin is used to check if the data is already exist in table
# input : cur  - db cursor point
#         data - condition data to be select from table, the format is [data1, data2], where data1, data2 is str
# output : result = 0 - data doesn't exist
#          result = 1 - data existes
def check_data_exist(cur, data):
    sql_cmd = ''' SELECT COUNT(*) FROM financial_data WHERE symbol=? AND date=? '''
    cur.execute(sql_cmd, data)
    result = cur.fetchone()[0]
    return result
    
    
# This functoin is used to get data by AlphaVantage free API and write the getting data to a csv file
# input : symbol - stocks name, available value are IBM and AAPL 
#         apikey - api key from AlphaVantage https://www.alphavantage.co/support/#api-key 
def get_financial_data(symbol, apikey):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&datatype=csv&apikey=%s' % (symbol, apikey)
    rqdata = rq.get(url)
    # Open csv file
    with open('financial_data_%s.csv' % (symbol), 'w') as fcsv:
        fcsv.write(rqdata.text)


# This functoin is used to get the data from csv file and then insert the unexpired data into table, duplicated data will be ignored
# input : con    - db connect point
#         cur    - db cursor point
#         symbol - stocks name, available value are IBM and AAPL
#         date   - expired date
def fill_financial_data(con, cur, symbol, date):
    if os.path.exists('financial_data_%s.csv' % (symbol)):
        # Read data from csv file
        financial_data = pd.read_csv('financial_data_%s.csv' % (symbol))
        os.remove('financial_data_%s.csv' % (symbol))
    else:
        print('Error : File financial_data_%s.csv doesn\'t exist\nNo data to be inserted into db' % (symbol))
        return
    # Get the line count
    nrows = financial_data.shape[0]
    # Do nothing if line less than 1
    if nrows < 1:
        print('Error : File financial_data_%s.csv doesn\'t have dada in it' % (symbol))
        return
    # Check the index should include ["timestamp","open","close","volume"]
    index = financial_data.loc[0,:].index
    if "timestamp" not in index or "open" not in index or "close" not in index or "volume" not in index:
        print('Error : File financial_data_%s.csv doesn\'t have available index in it\nNo data to be inserted into db' % (symbol))
        return
    # The symbol APPL is known as Apple Inc.
    if symbol == "AAPL":
        symbol = "Apple Inc."
    # Record how many data to be inserted into table
    ins_data = 0
    # Parse for each line in csv file
    for i in range(nrows):
        # Only the ["timestamp","open","close","volume"] value is needed
        ser = financial_data.loc[i, ["timestamp","open","close","volume"]]
        # Insert the data only when the date of data does not expired and the data does not existed in table
        if ser.values[0] > str(date) and check_data_exist(cur, [symbol, ser.values[0]]) == 0:
            insert_table(con, cur, [symbol, ser.values[0], ser.values[1], ser.values[2], str(ser.values[3])])
            ins_data += 1
    print('Insert [%s] line into table for stock [%s]' % (ins_data, symbol))


# This function is the main function
def main():
    # Get the API Key
    my_apikey = decrypt.main()
    if my_apikey is None:
        print('Error : The API Key file does not exist.\nPlease execute "\033[91mpython encryptAPIKEY.py\033[0m" to create the API Key file before running this program.')
        return
    # Get today date and expired date, the expired date is two week
    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    database = "financial_data.db"
    # Create a database connection
    connection = db_connection(database)
    with connection:
        # Create a database cursor
        cursor = connection.cursor()
        # Create the table if it is not existed
        if check_table(cursor) == 0:
            create_table(connection, cursor)
        # Delete the expired data if existed
        house_keeping(connection, cursor, two_weeks_ago)
        # Get the data from url to local csv
        get_financial_data("IBM", my_apikey)
        get_financial_data("AAPL", my_apikey)
        # Insert the data from csv to table
        fill_financial_data(connection, cursor, "IBM", two_weeks_ago)
        fill_financial_data(connection, cursor, "AAPL", two_weeks_ago)
        # Close database cursor
        cursor.close()
    # Close database connection
    connection.close()        
       

if __name__ == '__main__':
    main()