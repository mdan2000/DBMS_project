from enum import Enum

token = "1295127878:AAHl0ZuKuzRJ_9ATvZqrd1XlDnQf2EuOkNI"
server = 'tcp:2020hsedbmstest.database.windows.net' 
database = 'AdventureWorksLT' 
username = 'stud20' 
password = '!Student2020' 
connection_string = "DRIVER={ODBC Driver 17 for SQL Server};"\
"SERVER="+server+";"\
"DATABASE="+database+";"\
"UID="+username+";"\
"PWD="+ password

class States(Enum):
    NOTHING = 0,
    LANDLORD_ENTER_OK = 1,
    LANDLORD_ENTER_NAME = 2,
    TENANT_ENTER_OK = 3,
    TENANT_ENTER_NAME = 4,
    NEW_ANNOUNCEMENT_OK = 5,
    NEW_ANNOUNCEMENT_CITY = 6,
    NEW_ANNOUNCEMENT_DESCRIPTION = 7,
    NEW_ANNOUNCEMENT_PLEDGE = 8,
    NEW_ANNOUNCEMENT_SQUARE = 9,
    NEW_ANNOUNCEMENT_MIN_NIGHT = 10,
    NEW_ANNOUNCEMENT_MAX_NIGHT = 11,
    NEW_ANNOUNMENT_SUBURB = 12,
    NEW_ANNOUNCEMENT_LATITUDE = 13,
    NEW_ANNOUNCEMENT_LONGITUDE = 14,
    NEW_ANNOUNCEMENT_TYPE = 15,
    GET_ANNOUNCEMENT_ID = 16,
    SEND_ANNOUNCEMENT = 17,
    BOOKING_GET_ID = 18,
    BOOKING_GET_START_BOOKING = 19,
    BOOKING_GET_END_BOOKING = 20,
    LANDLORD_GET_BOOKING_ID = 21,
    MAKE_DECISION = 22,
    
