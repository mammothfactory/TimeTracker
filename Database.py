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
from datetime import datetime, timedelta
from time import sleep
import csv

# Internal modules
import GlobalConstants as GC

DEBUGGING =True

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
        
        # Create debuging logg
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS DebugLoggingTable (id INTEGER PRIMARY KEY, logMessage TEXT)''')
        
        self.conn.commit()


    def commit_changes(self):
        """ Commit data inserted into a table to the *.db database file 
        """
        self.conn.commit()


    def close_database(self):
        """ Close database to enable another sqlite3 instance to query a *.db database
        """
        self.conn.close()


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
            idToUpdate = results[0][0]
            self.cursor.execute("UPDATE UsersTable SET employeeId = ?, firstName = ?, lastName = ? WHERE id = ?", (id, first, last, idToUpdate))
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
        currentDateTime = datetime.now().isoformat(timespec="minutes")
        
        try:
            isoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has never clocked in before')
            self.cursor.execute("INSERT INTO CheckInTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))


        finally:
            if len(result) > 0:
                todayIsoString = datetime.now().isoformat(timespec="minutes")[0:10] 
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
                    

    def insert_check_out_table(self, id: int):
        """ Insert date and time (to current mintue) into CheckOutTable of database
            https://en.wikipedia.org/wiki/ISO_8601

        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
        """
        data = self.query_table("CheckOutTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        if GC.DEBUG_STATEMENTS_ON:  print(f'EMPLOYEE ID FILTER: {result}')

        isoString = '?'
        currentDateTime = datetime.now().isoformat(timespec="minutes")
        
        try:
            isoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has never clocked out before')
            self.cursor.execute("INSERT INTO CheckOutTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))


        finally:
            if len(result) > 0:
                todayIsoString = datetime.now().isoformat(timespec="minutes")[0:10] 
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
    
    
    def export_table_to_csv(self, table_name, output_file):
        # Connect to the SQLite database
        conn = sqlite3.connect('TimeReport.db')
        cursor = conn.cursor()

        # Fetch data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        # Get the column names
        column_names = [description[0] for description in cursor.description]

        # Write data to CSV file, overwriting old data
        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([i[0] for i in cursor.description])  # Write column names    #csv_writer.writerow(column_names)
            csv_writer.writerows(data)

        # Close the database connection
        conn.close()
        

    def is_date_between(startDatetimeObj, endDatetimeObj, dateToCheck) -> bool:
        return startDatetimeObj <= dateToCheck <= endDatetimeObj

if __name__ == "__main__":
    print("Testing Database.py")

    db = Database()
        
    db.insert_users_table("1001", "Blaze", "S")
    db.insert_users_table("1002", "Blair", "G")
    db.insert_users_table("9001", "User", "1")  
    db.insert_users_table("9025", "User", "1")
    csvFilename = datetime.now().isoformat(timespec="minutes")[0:10] + "_TimeReport.csv"
    db.export_table_to_csv("UsersTable", csvFilename)
    
    
    checkInErrors = db.insert_check_in_table(1001)
    print(checkInErrors)
    sleep(60)
    checkOutErrors = db.insert_check_out_table(1001)
    print(checkOutErrors)
    print(f'Hours = {db.calculate_time_delta(1001, "2023-08-02"):.4f}')
    
    
    
    #try expect ValueError: day is out of range for month

    databaseSearch = db.search_users_table("1001")
    if len(databaseSearch) > 0:
        print("Found employee ID in database")
        print(databaseSearch)

    db.close_database()
    