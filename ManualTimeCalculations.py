import sqlite3                              # https://docs.python.org/3/library/sqlite3.html
from datetime import datetime, timedelta 	# Create calendar dates & time objects https://docs.python.org/3/library/datetime.html

import schedule                             # Python functions periodicall https://schedule.readthedocs.io/en/stable/
import threading                            # https://schedule.readthedocs.io/en/stable/background-execution.html
from time import sleep                      # Import only the sleep function to pause prpgram execution 
import pytz 					            # World Timezone Definitions  https://pypi.org/project/pytz/

import csv

import GlobalConstants as GC

def get_date_time() -> datetime:
    """ Get date and time in Marianna, FL timezone, independent of location on server running code

    Returns:
        Datetime: 
    """
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


def calculate_time_delta(id: int, date: datetime) -> tuple:
        """ Calculate hours worked using clock in and clock out times from TimeReport.db SQLite database

        Args:
            id (int): Employeed ID
            date (datetime): Datetime object (e.g. "2023-08-27T05:26+00:00") 

        Returns:
            Tuple (elaspedHours, clockedIn, clockedOut):
            elaspedHours = Decimals hours between check in and check out time for an employee ID on a specific date
            clockedIn = True if an employee ID clocked IN using GUI, False otherwise
            clockedOut = True if an employee ID clocked OUT using GUI, False otherwise
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
            #print(f'Employee ID #{id} never clocked in on {dateToCalulate}')
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
            
        except IndexError:
            #print(f'Employee ID #{id} never clocked out on {dateToCalulate}')
            clockedOut = False
            datetimeCheckOutObject = None

        elaspedHours = 0
        if(not clockedIn and not clockedOut):
            elaspedHours = 0.0
        elif(not clockedIn and clockedOut):
            elaspedHours = 12.0
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
        
        return elaspedHours, clockedIn, clockedOut


def job():
    employeeIDs = [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025]
    
    dates = []
    for dayDelta in range(8, 1, -1):
        dates.append((get_date_time() - timedelta(days=dayDelta)).isoformat(timespec="minutes")[0:10])
    
    filename = dates[0] + '_' + dates[6] + '_LaborerTimeReport.csv'
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Employee ID', 'Total Hours', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'CheckIn Comment', 'CheckOut Comment'])
        for id in employeeIDs:
            dailyHours = []
            dailyCheckedIn = []
            dailyCheckedOut = []
            for day in dates:
                dateToCalculate = datetime.fromisoformat(day)
                hoursWorks, checkedIn, checkedOut = calculate_time_delta(id, dateToCalculate)
                dailyHours.append(round(hoursWorks, 4))
                dailyCheckedIn.append(checkedIn)
                dailyCheckedOut.append(checkedOut)
            
            totalHours = sum(dailyHours)
            inComment = 'Missed: '
            outComment = 'Missed: '
            dayOfWeek = ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat']
            for i in range(7):
                if dailyCheckedIn[i] == False:
                    inComment = inComment + dayOfWeek[i] + ' '
                if dailyCheckedOut[i] == False:
                    outComment = outComment + dayOfWeek[i] + ' '
            
            
            if totalHours == 0:
                data = [id, round(totalHours, 2), dailyHours[0], dailyHours[1], dailyHours[2], dailyHours[3], dailyHours[4], dailyHours[5], dailyHours[6], 'Missed: All Days', 'Missed: All Days']
            else:
                data = [id, round(totalHours, 2), dailyHours[0], dailyHours[1], dailyHours[2], dailyHours[3], dailyHours[4], dailyHours[5], dailyHours[6], inComment, outComment]
            
            writer.writerow(data)


def run_continuously(interval=2*GC.ONE_HOUR):
    """ Continuously run, while executing pending jobs at each elapsed time interval.
    
        @return cease_continuous_run: threading. Event which can be set to cease continuous run. Please note that it is
        intended behavior that run_continuously() does not run missed jobs*. For example, if you've registered a job that
        should run every minute and you set a continuous run interval of one hour then your job won't be run 60 times
        at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


if __name__ == "__main__":

    try:
        #job()
        
        schedule.every().day.at("02:00").do(job)
        ##schedule.every(10).sunday.at("02:00").do(job)
        stopRun = run_continuously()
        while True:
            sleep(60)
        
    except KeyboardInterrupt:
        stopRun.set()
        
        # Sleep so that only single 'Ctrl+C' is needed to exit program
        sleep(3)                    
        raise SystemExit
