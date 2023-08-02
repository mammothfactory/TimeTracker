#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
 __contact__    = "blazes@mfc.us"
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
import sys
from datetime import datetime, time

# Internally developed modules
import GlobalConstants as GC              # Global constants used across MainHouse.py, HouseDatabase.py, and PageKiteAPI.py
from Database import Database             # Store non-Personally Identifiable Information of employee ID's and timestamps
from Email import Email

# Browser base GUI framework to build and display a user interface mobile, PC, and Mac
# https://nicegui.io/
from nicegui import app, ui
from nicegui.events import MouseEventArguments

DEBUG_STATEMENTS_ON = True
ELEVEN_PM = time(23, 0, 0)


if __name__ == "__main__":
    db = Database()
    

    current_time = datetime.now().time()
    
    # Create a time object for 11 PM
    
    
    if current_time > ELEVEN_PM:
        csvFilename = datetime.now().isoformat(timespec="minutes")[0:10] + "_TimeReport.csv"
        db.export_table_to_csv("UsersTable", csvFilename)