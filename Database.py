#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.1.0"
"""

# Disable PyLint linting messages
# https://pypi.org/project/pylint/
# pylint: disable=line-too-long
# pylint: disable=invalid-name

# Standard Python libraries
import sqlite3

from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html
from time import sleep
import pytz 					                # World Timezone Definitions  https://pypi.org/project/pytz/

import os
import csv

# Internal modules
import GlobalConstants as GC

DEBUGGING = True

class Database:
    """ Store non-Personally Identifiable Information in SQLite database
    """

    def __init__(self):
        """ Constructor to initialize an Database object
        """
        # Connect to the database (create if it doesn't exist)
        self.conn = sqlite3.connect('TimeReport.db')
        self.cursor = self.conn.cursor()

        # Create four tables in TimeReport.db for user name and time logging data storage
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS UsersTable (id INTEGER PRIMARY KEY, employeeId INTEGER, firstName TEXT, lastName TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CheckInTable (id INTEGER PRIMARY KEY, employeeId INTEGER, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CheckOutTable (id INTEGER PRIMARY KEY, employeeId INTEGER, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS WeeklyReportTable (id INTEGER PRIMARY KEY, fullname TEXT, employeeId INTEGER, totalHours INTEGER, day6 INTEGER, day0 INTEGER, day1 INTEGER, day2 INTEGER, day3 INTEGER, day4 INTEGER, day5 INTEGER, inComments TEXT, outComments TEXT)''')
        
        # Create debuging logg
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS DebugLoggingTable (id INTEGER PRIMARY KEY, logMessage TEXT)''')
        
        self.conn.commit()
        
        self.insert_users_table("1001", "Blaze", "S")
        self.insert_users_table("1002", "Blair", "G")
        self.insert_users_table("1003", "Brandy", "K")
        self.insert_users_table("1005", "J", "R")
        
        self.insert_users_table("9001", "User", "1")  
        self.insert_users_table("9002", "User", "1")
        self.insert_users_table("9003", "User", "1") 
        self.insert_users_table("9004", "User", "1") 
        self.insert_users_table("9005", "User", "1") 
        self.insert_users_table("9006", "User", "1") 
        self.insert_users_table("9007", "User", "1") 
        self.insert_users_table("9008", "User", "1") 
        self.insert_users_table("9009", "User", "1") 
        self.insert_users_table("9010", "User", "1") 
        
        self.insert_users_table("9011", "User", "1")  
        self.insert_users_table("9012", "User", "1")
        self.insert_users_table("9013", "User", "1") 
        self.insert_users_table("9014", "User", "1") 
        self.insert_users_table("9015", "User", "1") 
        self.insert_users_table("9016", "User", "1") 
        self.insert_users_table("9017", "User", "1") 
        self.insert_users_table("9018", "User", "1") 
        self.insert_users_table("9019", "User", "1") 
        self.insert_users_table("9020", "User", "1")
    
        self.insert_users_table("9021", "User", "1")  
        self.insert_users_table("9022", "User", "1")
        self.insert_users_table("9023", "User", "1") 
        self.insert_users_table("9024", "User", "1") 
        self.insert_users_table("9025", "User", "1") 
        self.insert_users_table("9026", "User", "1") 
        self.insert_users_table("9027", "User", "1") 
        self.insert_users_table("9028", "User", "1") 
        self.insert_users_table("9029", "User", "1") 
        self.insert_users_table("9030", "User", "1")  
        


    def commit_changes(self):
        """ Commit data inserted into a table to the *.db database file 
        """
        self.conn.commit()


    def close_database(self):
        """ Close database to enable another sqlite3 instance to query a *.db database
        """
        self.conn.close()


    def getDateTime(self):
        tz = pytz.timezone('America/Chicago')
        zulu = pytz.timezone('UTC')
        now = datetime.now(tz)
        if now.dst() == timedelta(0):
            now = datetime.now(zulu) - timedelta(hours=6)
            #print('Standard Time')

        else:
            now = datetime.now(zulu) - timedelta(hours=5)
            #print('Daylight Savings')   
            
        return now 



    def query_table(self, tableName: str):
        """ Return every row of a table from a *.db database

        Args:
            tableName (String): Name of table in database to query

        Returns:
            List: Tuples from a table, where each row in table is a tuple length n
        """
        sqlStatement = f"SELECT * FROM {tableName}"
        self.cursor.execute(sqlStatement)

        result = self.cursor.fetchall()

        return result
    
    
    def insert_users_table(self, id: int, first: str, last: str):
        """ Insert employee ID, first name, and last name first initial into the User Table if employee ID is unqiue, otherwise update name
        
        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
            first (str): Full first name (or nickname) of employee
            last (str): The first initial of employee last name to make data less Personally Identifiable Information 
        """
        results = self.search_users_table(id)

        if len(results) > 0:
            idPrimaryKeyToUpdate = results[0][0]
            self.cursor.execute("UPDATE UsersTable SET employeeId = ?, firstName = ?, lastName = ? WHERE id = ?", (id, first, last, idPrimaryKeyToUpdate))
        else:
            self.cursor.execute("INSERT INTO UsersTable (employeeId, firstName, lastName) VALUES (?, ?, ?)", (id, first, last))

        self.commit_changes()

    
    def insert_check_in_table(self, id: int) -> tuple:
        """ Insert date and time (to current mintue) into CheckInTable of database
            https://en.wikipedia.org/wiki/ISO_8601

        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
        """
        data = self.query_table("CheckInTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        if GC.DEBUG_STATEMENTS_ON:  print(f'EMPLOYEE ID FILTER: {result}')

        isoString = '?'
        currentDateTime = self.getDateTime().isoformat(timespec="minutes")
        
        try:
            isoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has never clocked in before')
            self.cursor.execute("INSERT INTO CheckInTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))


        finally:
            if len(result) > 0:
                todayIsoString = self.getDateTime().isoformat(timespec="minutes")[0:10] 
                finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(todayIsoString), result))
                if GC.DEBUG_STATEMENTS_ON: print(f'TIMESTAMP ID FILTER: {finalResult}')
    
                if len(finalResult) > 0:
                    nameResults = self.search_users_table(str(id))
                    englishError = f'{nameResults[0][2]} {nameResults[0][3]} you already clocked in today'
                    spanishError = f'{nameResults[0][2]} {nameResults[0][3]} ya has fichado hoy'
                    return englishError, spanishError
                else:
                    if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {finalResult} since employee didnt clock in today')
                    self.cursor.execute("INSERT INTO CheckInTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))
                    
        self.commit_changes()
                    

    def insert_check_out_table(self, id: int) -> tuple:
        """ Insert date and time (to current mintue) into CheckOutTable of database
            https://en.wikipedia.org/wiki/ISO_8601

        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
        """
        data = self.query_table("CheckOutTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        if GC.DEBUG_STATEMENTS_ON:  print(f'EMPLOYEE ID FILTER: {result}')

        isoString = '?'
        currentDateTime = self.getDateTime().isoformat(timespec="minutes")
        
        try:
            isoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has never clocked out before')
            self.cursor.execute("INSERT INTO CheckOutTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))


        finally:
            if len(result) > 0:
                todayIsoString = self.getDateTime().isoformat(timespec="minutes")[0:10] 
                finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(todayIsoString), result))
                if GC.DEBUG_STATEMENTS_ON: print(f'TIMESTAMP ID FILTER: {finalResult}')
    
                if len(finalResult) > 0:
                    nameResults = self.search_users_table(str(id))
                    englishError = f'{nameResults[0][2]} {nameResults[0][3]} you already clocked out today'
                    spanishError = f'{nameResults[0][2]} {nameResults[0][3]} ya saliste hoy'
                    return englishError, spanishError
                else:
                    if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {finalResult} since employee didnt clock out today')
                    self.cursor.execute("INSERT INTO CheckOutTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))
      
        self.commit_changes()


    def insert_debug_logging_table(self, debugText: str):
        """ 

        Args:
            debugText (str): ERROR: or WARNING: text message to log 
        """
        self.cursor.execute("INSERT INTO DebugLoggingTable (logMessage) VALUES (?)", (debugText,))
        self.commit_changes()
        


    def search_users_table(self, searchTerm: str):
        """ Search UsersTable table for every occurrence of a string

        Args:
            searchTerm (str): _description_

        Returns:
            List: Of Tuples from a UsersTable, where each List item is a row in the table containing the exact search term
        """
        self.cursor.execute("SELECT * FROM UsersTable WHERE employeeId LIKE ?", ('%' + searchTerm + '%',))
        results = self.cursor.fetchall()

        return results
    
    def insert_weekly_report_table(self, id: int, dateToCalulate: datetime):
        """ Build a table using the following rules:
            Default to 12 hours if employee forgets to clock OUT - But also flag that this occured
            Default to 0 hours if employee forgets to clock IN, but also allow for clock out with TODO start time  
        

        Args:
            id (int): _description_
            dateToCalulate (datetime): _description_
        """
        # data = self.query_table("WeeklyReportTable") 
        # self.cursor.execute('''CREATE TABLE IF NOT EXISTS WeeklyReportTable (id INTEGER PRIMARY KEY, fullname TEXT, employeeId INTEGER, day0 INTEGER, day1 INTEGER, day2 INTEGER, day3 INTEGER, day4 INTEGER, day5 INTEGER, day6 INTEGER, inComments TEXT, outComments TEXT)''')
        # self.cursor.execute("INSERT INTO CheckOutTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))
        # self.cursor.execute("UPDATE UsersTable SET employeeId = ?, firstName = ?, lastName = ? WHERE id = ?", (id, first, last, idPrimaryKeyToUpdate))
        
        try:
            # Get the day of the week (0=Monday, 1=Tuesday, ..., 6=Sunday)
            dayOfWeek = dateToCalulate.weekday()
            if Database.DEBUGGING: 
                dayOfWeek = GC.MONDAY
                currentTime = time(22, 45, 0)
                #currentTime = time(23, 22, 0)
                #currentTime = time(23, 59, 0)
                #currentTime = time(24, 0, 0)
                #currentTime = time(1, 2, 0)
                #currentTime = time(2, 59, 0)
                #currentTime = time(3, 11, 0)
            
            dailyHours = self.calculate_time_delta(id, dateToCalulate) 
            
            results = self.search_users_table(id)
            if len(results) > 0:
                idPrimaryKeyToUpdate = results[0][0]
                
                if dayOfWeek == GC.SUNDAY: 
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day6 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.MONDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day0 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.TUESDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day1 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.WEDNESDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day2 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.THURSDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day3 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.FRIDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day4 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.SATURDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET employeeId = ?, day5 = ? WHERE id = ?", (id, dailyHours, idPrimaryKeyToUpdate))
               
                
                self.commit_changes()
            else:
                print("INVALID USER ID")
                    
        except ValueError:
            self.insert_debug_logging_table(f'Invalid date format when generating weekly report on {dateToCalulate}')
            
        except IndexError:
            print("INVALID USER ID")

    
    def calculate_time_delta(self, id: int, dateToCalulate: str) -> float:

        data = self.query_table("CheckInTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        try:
            checkInIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            self.insert_debug_logging_table(f'Employee ID #{id} never clocked in on {dateToCalulate}')
        except IndexError:
            return 0.0

        data = self.query_table("CheckOutTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        try:
            checkOutIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            self.insert_debug_logging_table(f'Employee ID #{id} never clocked out on {dateToCalulate}')
        except IndexError:
            return 0.0

        # Convert the ISO strings to datetime objects
        datetimeCheckInObject = datetime.fromisoformat(checkInIsoString)
        datetimeCheckOutObject = datetime.fromisoformat(checkOutIsoString)

        # Perform the subtraction and convert to decimal hours rounded to two decimal points
        timeDeltaObject = datetimeCheckOutObject - datetimeCheckInObject
        elaspedSeconds = timeDeltaObject.seconds
        elaspedHours = elaspedSeconds / 3600.0
        
        return elaspedHours
    
    
    def export_table_to_csv(self, tableNames):
        """ Creates a filename assuming that the date that this code runs is a Monday

        Args:
            table_name (_type_): _description_
        """
        # Connect to the SQLite database
        conn = sqlite3.connect('TimeReport.db')
        cursor = conn.cursor()

        for table in tableNames:
            try:
                # Fetch data from the table
                cursor.execute(f"SELECT * FROM {table}")
                data = cursor.fetchall()
            
            except sqlite3.OperationalError:
                pass #db.insert_debug_logging_table(f'No table named {table} when converting table to CSV in Database.export_table_to_csv() function')

            finally:   
                # Create a .csv filename base on (Monday - 8 days) to (Monday - 2 days) to create for example 2023-08-01_2023-08-07_LaborerTimeReport
                lastSunday = (self.getDateTime() - timedelta(days=8)).isoformat(timespec="minutes")[0:10]
                lastSaturday = (self.getDateTime() - timedelta(days=2)).isoformat(timespec="minutes")[0:10]
                
                currentDirectory = os.getcwd()
                nextDirectory = os.path.join(currentDirectory, 'TimeCardReports')
                if not os.path.exists(nextDirectory):
                    os.makedirs(nextDirectory)
                
                if table == "WeeklyReportTable":
                    columnNames = ["Full Name", "Employee ID", "Total Hours", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Check In Comments", "Check Out Comments"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_LaborerTimeReport.csv"  
                    filePath = os.path.join(nextDirectory, outputFilename)
                    
                
                elif table == "CheckInTable":
                    columnNames = ["Full Name", "Employee ID", "Clock IN Timestamp"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_ClockInTimes.csv"
                    filePath = os.path.join(nextDirectory, outputFilename)

                        
                elif table == "CheckOutTable":
                    columnNames = ["Full Name", "Employee ID", "Clock OUT Timestamp"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_ClockOutTimes.csv" 
                    filePath = os.path.join(nextDirectory, outputFilename)
                
                else:
                    print(f'Table Name {table} conversion not implemented')
                 
                    with open(filePath, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(columnNames[0:12])
                        for row in data:
                            csv_writer.writerow(row[1:])
                            
                    csvfile.close()

        # Close the database connection
        conn.close()
        
        

    def is_date_between(startDatetimeObj, endDatetimeObj, dateToCheck) -> bool:
        return startDatetimeObj <= dateToCheck <= endDatetimeObj

if __name__ == "__main__":
    print("Testing Database.py")

    db = Database()

    db.export_table_to_csv(["WeeklyReportTable", "CheckInTable", "CheckOutTable"])
    
    
    checkInErrors = db.insert_check_in_table(1001)
    print(checkInErrors)
    sleep(3)
    checkOutErrors = db.insert_check_out_table(1001)
    print(checkOutErrors)
    
    today = db.getDateTime().isoformat(timespec="minutes")[0:10]
    print(f'Hours = {db.calculate_time_delta(1001, today):.4f}')
    
    
    
    #try expect ValueError: day is out of range for month

    databaseSearch = db.search_users_table("1001")
    if len(databaseSearch) > 0:
        print("Found employee ID in database")
        print(databaseSearch)

    db.close_database()
    