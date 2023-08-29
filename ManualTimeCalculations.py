# Standard Python libraries
import sqlite3


from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html
from time import sleep
import pytz 					                # World Timezone Definitions  https://pypi.org/project/pytz/

import os
import csv

# Internal modules
import GlobalConstants as GC
        
def calculate_time_delta(id: int, date: datetime) -> float:
        """_summary_

        Args:
            id (int): _description_
            dateToCalulate (str): _description_

        Returns:
            float: Decimals hours between check in and check out time for a specific employee ID on a specific date
        """
        clockedIn = True
        clockedOut = True
        
        conn = sqlite3.connect('TimeReport.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM CheckInTable")
        data = cursor.fetchall()
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        dateToCalulate = date.isoformat(timespec="minutes")[0:10]
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        #print(finalResult)
        try:
            checkInIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            datetimeCheckInObject = datetime.fromisoformat(checkInIsoString)        # Convert the ISO strings to datetime objects
            
        except IndexError:
            print(f'Employee ID #{id} never clocked in on {dateToCalulate}')
            clockedIn = False
            datetimeCheckInObject = None

        cursor.execute("SELECT * FROM CheckOutTable")
        data = cursor.fetchall()
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        #print(finalResult)
        try:
            checkOutIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            datetimeCheckOutObject = datetime.fromisoformat(checkOutIsoString)      # Convert the ISO strings to datetime objects
            datetimeCheckOutObject = None
            
        except IndexError:
            print(f'Employee ID #{id} never clocked out on {dateToCalulate}')
            clockedOut = False

        elaspedHours = 0
        if(not clockedIn and not clockedOut):
            elaspedHours = 0.0
        elif(clockedIn and not clockedOut):
            elaspedHours = 12.0
        elif(not clockedIn and not clockedOut):
            elaspedHours = 12.0
        else: 
            if datetimeCheckInObject and datetimeCheckOutObject:             
                # Perform the absolute value subtraction (timeDeltaObject is NEVER negative)
                timeDeltaObject = datetimeCheckOutObject - datetimeCheckInObject
                elaspedSeconds = timeDeltaObject.seconds
                elaspedHours = elaspedSeconds / 3600.0
        
        return elaspedHours
   
if __name__ == "__main__":
    id = 1001
    date = datetime.fromisoformat("2023-08-22")
    print(calculate_time_delta(id, date))
    
    date = datetime.fromisoformat("2023-08-23")
    print(calculate_time_delta(id, date))
    
    date = datetime.fromisoformat("2023-08-24")
    print(calculate_time_delta(id, date))
    
    date = datetime.fromisoformat("2023-08-25")
    print(calculate_time_delta(id, date))
    
    date = datetime.fromisoformat("2023-08-26")
    print(calculate_time_delta(id, date))