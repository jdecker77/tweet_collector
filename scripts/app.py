
'''
Imports
-------------------------------------------------------------------------------------------
'''
# Python
import sys

# 3rd Party
import pandas as pd

# Local 
import schedule


'''
App
-------------------------------------------------------------------------------------------
'''
# Define a new collection interval
def GetStartParams():
    params = {}

    year = int(input("Enter 4 digit year: "))
    while year < 2019 or year > 2020:
        print("Invalid input")
        year = int(input("Enter 4 digit year: "))
    params['year'] = year

    month = int(input("Enter month: "))
    while month < 1 or month > 12:
        print("Invalid input")
        month = int(input("Enter month: "))
    params['month'] = month

    day = int(input("Enter day: "))
    while day < 1 or day > 31:
        print("Invalid input")
        day = int(input("Enter day: "))
    params['day'] = day

    # Enter number of days to collect 
    collection_interval = int(input("Enter number of days to collect: "))
    while day < 1 or day > 31:
        print("Invalid input")
    params['collection_interval'] = collection_interval

    # Add an identifier for the interval
    interval_identifier = input("Enter unique name for interval: ")
    params['interval_identifier'] = interval_identifier 

    return params

# Locate an existing set object by month/day
def GetExistingParams():
    params = {}

    year = int(input("Enter 4 digit year: "))
    while year < 2019 or year > 2020:
        print("Invalid input")
        year = int(input("Enter 4 digit year: "))
    params['year'] = year

    month = int(input("Enter month: "))
    while month < 1 or month > 12:
        print("Invalid input")
        month = int(input("Enter month: "))
    params['month'] = month

    day = int(input("Enter day: "))
    while day < 1 or day > 31:
        print("Invalid input")
        day = int(input("Enter day: "))
    params['day'] = day

    return params

# Output terminal ui for menu selection.
def main():

    done = False
    while not done:

        print("\n")
        ui = int(input("Enter 0 to exit, 1 to create new sets, 2 to load existing sets: "))
        
        while ui < 0 or ui > 2:
            print("invalid Input")
            ui = int(input("Enter 0 to exit, 1 to start over, 2 to load existing sets: "))
        
        if ui == 0:
            done = True
        elif ui == 1:
            params = GetStartParams()
            user_schedule = pd.read_excel('../resources/schedule_B.xlsx')
            schedule.MakeSets(
                params['year'],
                params['month'],
                params['day'],
                params['collection_interval'],
                params['interval_identifier'],
                user_schedule
            )
        elif ui == 2:
            params = GetExistingParams()
        
        # Show schedule. Allow user to collect or select again
        if not done:
            try:
                schedule.PreviewSchedule(params['month'],params['day'])
                print("\n")
                run = int(input("Enter 0 to start over or 1 to run schedule: "))
                while run < 0 or run > 1:
                    print("Invalid Input")
                    run = int(input("Enter 0 to start over or 1 to run schedule: "))
                if run == 1:
                    print("\n")
                    print("Select a collection algorithm.")
                    collector = int(input("Enter 0 to exit, 1 to run machine learning collector, 2 to run network collector: "))
                    while collector < 0 or collector > 2:
                        print("Invalid Input")
                        collector = int(input("Enter 0 to exit, 1 to run machine learning collector, 2 to run network collector: "))
                    if collector == 1:
                        print("Starting ML Connection")
                        # schedule.RunMLCollector(params['month'],params['day'])
                    elif collector == 2:
                        print("Starting Network Connection")
                        # schedule.RunNWCollector(params['month'],params['day'])
            except Exception as e:
                print(e, file=sys.stderr)
                print('Could not find a file with that date.')
main()

