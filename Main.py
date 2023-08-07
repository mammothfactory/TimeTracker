#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
 __contact__   = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.0.1"
__doc__        = "Generate a Progressive Web App GUI to log employee check-in and check-out times"
"""

# Disable PyLint linting messages that seem unuseful
# https://pypi.org/project/pylint/
# pylint: disable=invalid-name
# pylint: disable=global-statement

# Standard Python libraries
from datetime import datetime, time # Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html
import re                           # Regular Expression matching operations https://docs.python.org/3/library/re.html

# Internally developed modules
from PageKiteAPI import *                           # Create & delete custom subdomains for reverse proxy to tunnel
import GlobalConstants as GC              # Global constants used across MainHouse.py, HouseDatabase.py, and PageKiteAPI.py
from Database import Database             # Store non-Personally Identifiable Information of employee ID's and timestamps

# Browser base GUI framework to build and display a user interface mobile, PC, and Mac
# https://nicegui.io/
from nicegui import app, ui
from nicegui.events import MouseEventArguments

# Load environment variables for usernames, passwords, & API keys
# https://pypi.org/project/python-dotenv/
from dotenv import dotenv_values

THREE_AM = time(3, 0, 0)
ELEVEN_PM = time(23, 0, 0)
clock = ui.html().classes("self-center")

sanitizedID = ''
validEmployeeID = ''

def build_svg() -> str:
    """ Create an 800 x 800 pixel clock in HTML / SVG
        https://de.m.wikipedia.org/wiki/Datei:Station_Clock.svg
        
    Args:
        NONE

    Returns:
        str: Valid HTML to create an analog clock
    """
    now = datetime.now()
    return f'''
        <svg width="800" height="800" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <circle cx="400" cy="400" r="200" fill="#fff"/>
            <use transform="matrix(-1,0,0,1,800,0)" xlink:href="#c"/>
            <g id="c">
                <g id="d">
                    <path d="m400 40v107" stroke="#000" stroke-width="26.7"/>
                    <g id="a">
                        <path d="m580 88.233-42.5 73.612" stroke="#000" stroke-width="26.7"/>
                        <g id="e">
                            <path id="b" d="m437.63 41.974-3.6585 34.808" stroke="#000" stroke-width="13.6"/>
                            <use transform="rotate(6 400 400)" xlink:href="#b"/>
                        </g>
                        <use transform="rotate(12 400 400)" xlink:href="#e"/>
                    </g>
                    <use transform="rotate(30 400 400)" xlink:href="#a"/>
                    <use transform="rotate(60 400 400)" xlink:href="#a"/>
                </g>
                <use transform="rotate(90 400 400)" xlink:href="#d"/>
            </g>
            <g transform="rotate({250 + now.hour / 12 * 360} 400 400)">
                <path d="m334.31 357.65-12.068 33.669 283.94 100.8 23.565-10.394-13.332-24.325z"/>
            </g>
            <g transform="rotate({117 + now.minute / 60 * 360} 400 400)">
                <path d="m480.73 344.98 11.019 21.459-382.37 199.37-18.243-7.2122 4.768-19.029z"/>
            </g>
            <g transform="rotate({169 + now.second / 60 * 360} 400 400)">
                <path d="m410.21 301.98-43.314 242.68a41.963 41.963 0 0 0-2.8605-0.091 41.963 41.963 0 0 0-41.865 42.059 41.963 41.963 0 0 0 30.073 40.144l-18.417 103.18 1.9709 3.9629 3.2997-2.9496 21.156-102.65a41.963 41.963 0 0 0 3.9771 0.1799 41.963 41.963 0 0 0 41.865-42.059 41.963 41.963 0 0 0-29.003-39.815l49.762-241.44zm-42.448 265.56a19.336 19.336 0 0 1 15.703 18.948 19.336 19.336 0 0 1-19.291 19.38 19.336 19.336 0 0 1-19.38-19.291 19.336 19.336 0 0 1 19.291-19.38 19.336 19.336 0 0 1 3.6752 0.3426z" fill="#a40000"/>
            </g>
        </svg>
    '''

def clock_x(direction: int, sanitizedID: str):
    """ Perform database insert 

    Args:
        direction (CONSTANT int):Define function as clock IN or clock OUT method
        sanitizedID (str): Global sanitized number entered into Number text  box
    """
    
    if invalidIdLabel.visible == False and len(sanitizedID) == GC.VALID_EMPLOYEE_ID_LENGTH:
        if direction == GC.CLOCK_IN:
            clockedInLabel.set_text(f'{sanitizedID} - REGISTRO EN (CLOCKED IN)')
            db.insert_check_in_table(sanitizedID)
        elif direction == GC.CLOCK_OUT:
            clockedOutLabel.set_text(f'{sanitizedID} - RELOJ DE SALIDA (CLOCK OUT)')
            db.insert_check_out_table(sanitizedID)
        
        clockedInLabel.visible = True
    else:
       tryAgainLabel.visible = True
    
    inputBox.set_value(None)                          # Clear user input box after set_value('') doesn't work :)  
                         

def sanitize_employee_id(inputText: str) -> str:
    """ Convert all bad user input to valid ouput and update GUI label visibility to control datatbase writes

    Args:
        inputText (str): Raw user input with possible errors

    Returns:
        str: A string with all blank spaces and non-digit characters removed
    """
    global sanitizedID

    if int(inputText) > 9999 or int(inputText) < 0:
        invalidIdLabel.visible = True
        return 'ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)'
    else:
       invalidIdLabel.visible = False
    
    if inputText == '0':
        sanitizedID = ''
    else:
        sanitizedID = str(int(inputText))

    return sanitizedID


def generate_report(db):
    """ Generate EXCEL document every monday at 3 am
        Work week starts Sunday at 12:01 am and repeats every 7 days
        Work week ends Saturday at 11:59 pm and repeats every 7 days
        Assumes 12 hour work day at 11 pm if an employee only clocks IN but forgets to clock out
        Back calculates 12 hour work day using the time an employee clocks OUT if no clocking IN exists

    Args:
        db (sqlite): *.db database file containing a table called "WeeklyReportTable"
    """
    currentDateObj = datetime.now()
    dayOfWeek = currentDateObj.weekday()
    currentTime = currentDateObj.time()
    #if DEBUGGING: dayOfWeek = GC.MONDAY

    if dayOfWeek == GC.MONDAY and (ELEVEN_PM < currentTime and currentTime < THREE_AM):
        db.export_table_to_csv("WeeklyReportTable")


if __name__ in {"__main__", "__mp_main__"}:
    
    # https://computingforgeeks.com/how-to-install-python-latest-debian/
    
    config = dotenv_values()
    
    db = Database()
    #command = ['python3', 'pagekite.py', f'{GC.LOCAL_HOST_PORT_FOR_GUI}', 'timetracker.pagekite.me']

    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedInLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedOutLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: tryAgainLabel.set_visibility(False))
    ui.timer(GC.DATABASE_DAILY_REPORT_UPDATE_TIME, lambda: generate_report(db))
    ui.timer(GC.CLOCK_UPDATE_TIME, lambda: clock.set_content(build_svg()))
    
    invalidIdLabel = ui.label('ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)').style("color: red; font-size: 200%; font-weight: 300").classes("self-center")
    invalidIdLabel.visible = False
    
    inputBox = ui.number(label='Ingrese su identificación de empleado', placeholder='Enter your Employee ID', value='', \
                        format='%i', \
                        step='1000', \
                        on_change=lambda e: invalidIdLabel.set_text(sanitize_employee_id(e.value)), \
                        validation={'ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)': lambda value: int(sanitizedID) <= 9999})
    
    inputBox.classes("self-center").style("padding: 40px 0px; width: 800px; font-size: 30px;").props('clearable')

    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        with ui.button(on_click=lambda e: clock_x(GC.CLOCK_IN, sanitizedID), color="green").classes("relative  h-32 w-96"):
            ui.label('RELOJ EN (CLOCK IN) ㅤ').style('font-size: 150%; font-weight: 300')
            ui.icon('login')
        
        with ui.button(on_click=lambda e: clock_x(GC.CLOCK_OUT, sanitizedID), color="red").classes("relative  h-32 w-96"):
            ui.label('RELOJ DE SALIDA (CLOCK OUT) ㅤ').style("font-size: 150%; font-weight: 300")
            ui.icon('logout')
    
    clockedInLabel = ui.label(f'{validEmployeeID} - REGISTRO EN (CLOCKED IN)').style("color: green; font-size: 400%; font-weight: 300").classes("self-center")
    clockedOutLabel = ui.label(f'{validEmployeeID} - FINALIZADO (CLOCKED OUT)').style("color: red; font-size: 400%; font-weight: 300").classes("self-center")    
    tryAgainLabel = ui.label('INTENTAR OTRA VEZ (TRY AGAIN)').style("color: red; font-size: 400%; font-weight: 300").classes("self-center")
    
    ui.run(native=GC.RUN_ON_NATIVE_OS, port=GC.LOCAL_HOST_PORT_FOR_GUI)
    