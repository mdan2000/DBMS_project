import pyodbc
import config
import datetime


def get_id_with_city(city):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT id_post FROM Houses.announcement WHERE id_city = {city}')
    data = []
    for row in cursor:
        data.append(row[0])
    return data

def get_city_id(city):
    if exists_row("Houses.city", "name", "'" + city + "'"):
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'SELECT id_city FROM Houses.city WHERE name = \'{city}\'')
        id_city = 0
        for row in cursor:
            id_city = row[0]
        return id_city
    else:
        0

def from_table_in_row_get_val(table, pk, pk_val, col):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT {col} FROM {table} WHERE {pk} = {pk_val}')
    data = []
    for row in cursor:
        data = row[0]
    return data

def get_announcement_by_id(id_post):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT * FROM Houses.announcement WHERE id_post = {id_post} AND revelance = 1')
    data = []
    for row in cursor:
        data = row
    return data

def get_state(chat_id):
    if not exists_row("temp_state", "chat_id", chat_id):
        return 0
    else:
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'SELECT state_id FROM temp_state WHERE chat_id = {chat_id}')
        state = 0
        for row in cursor:
            state = row[0]
        return state

def make_decision(id_owner, decision):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT id_booking FROM dbo.decision WHERE id_owner = {id_owner}')
    id_booking = 0
    for row in cursor:
        id_booking = row[0]
    cursor.execute(f'SELECT id_client FROM Houses.booking_date WHERE id_booking = {id_booking}')
    id_client = 0
    for row in cursor:
        id_client = row[0]
    cursor.execute(f'UPDATE Houses.booking_date SET Houses.booking_date.confirmation = {decision} WHERE id_booking = {id_booking}')
    cursor.commit()
    return id_client, id_booking

def new_decision(id_owner, id_booking):
    cursor = pyodbc.connect(config.connection_string).cursor()
    if exists_row("dbo.decision", "id_owner", id_owner):
        cursor.execute(f'UPDATE dbo.decision SET dbo.decision.id_booking = {id_booking} WHERE id_owner = {id_owner}')
    else:
        cursor.execute(f'INSERT INTO dbo.decision(id_owner, id_booking) values ({id_owner}, {id_booking})')
    cursor.commit()

def copy_to_announcement_from_temp(chat_id):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT * FROM dbo.temp_announcement WHERE id_owner = {chat_id}')
    vals = []
    for row in cursor:
        vals = row
    cursor.execute(f'INSERT INTO Houses.announcement(text_description, average_rating, number_of_review,\
        min_nights, max_nights, pledge, cost_per_night, type_house, square, latitude, longitude, \
        revelance, id_owner, id_suburb, id_city) values (\'{vals[1]}\', 50, 0, {vals[2]}, {vals[3]}, {vals[4]}, \
        {vals[5]}, \'{vals[6]}\', {vals[7]}, {vals[8]}, {vals[9]}, 1, {vals[0]}, {vals[10]}, {vals[11]})')
    cursor.commit()

def check_booking(id_owner, id_booking):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT * FROM Houses.booking_date WHERE id_owner = {id_owner} AND id_booking = {id_booking}')
    count = 0
    for row in cursor:
        count += 1
    return count > 0

def copy_to_booking_from_temp(chat_id):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT * FROM dbo.temp_booking WHERE id_client = {chat_id}')
    vals = []
    for row in cursor:
        vals = row
    cursor.execute(f'INSERT INTO Houses.booking_date(start_booking, end_booking, confirmation,\
        canceling, id_owner, id_client, id_post) values (\'{vals[0]}\', \'{vals[1]}\', 0, 0, {vals[2]}, {vals[3]}, \
        {vals[4]})')
    cursor.commit()
    cursor.execute(f'SELECT id_booking FROM Houses.booking_date WHERE start_booking = \'{vals[0]}\' AND \
        end_booking = \'{vals[1]}\' AND id_owner = \'{vals[2]}\' AND id_client = \'{vals[3]}\' AND id_post = \'{vals[4]}\'')
    id_booking = 0
    for row in cursor:
        id_booking = row[0]
    return vals[2], vals[4], vals[0], vals[1], id_booking

def in_table_in_row_in_col_set_val(table, pk, val_pk, col, val):
    cursor = pyodbc.connect(config.connection_string).cursor()
    if type(val) is str:
        cursor.execute(f'UPDATE {table} SET {table}.{col} = \'{val}\' WHERE {pk} = {val_pk}')
    else:
        cursor.execute(f'UPDATE {table} SET {table}.{col} = {val} WHERE {pk} = {val_pk}')
    cursor.commit()

def from_table_get_all_values_of_col(table, col):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT {col} FROM {table}')
    vals = []
    for row in cursor:
        vals.append(row[0])
    return vals

def set_start_date(chat_id, start_date):
    in_table_in_row_in_col_set_val("dbo.temp_booking", "id_client", chat_id, "start_booking", str(start_date))

def set_end_date(chat_id, end_date):
    in_table_in_row_in_col_set_val("dbo.temp_booking", "id_client", chat_id, "end_booking", str(end_date))

def set_new_booking(id_post, chat_id):
    id_owner = from_table_in_row_get_val("Houses.announcement", "id_post", id_post, "id_owner")
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f"INSERT INTO dbo.temp_booking(start_booking, end_booking, id_owner, id_client, id_post)\
        values(NULL, NULL, {id_owner}, {chat_id}, {id_post})")
    cursor.commit()

def exists_announcement(id_post):
    return exists_row("Houses.announcement", "id_post", id_post)

def exists_row(table, pk, pk_val):
    cursor = pyodbc.connect(config.connection_string).cursor()
    count_states_id = 0
    cursor.execute(f'SELECT {pk} FROM {table} WHERE {pk} = {pk_val}')
    count = 0
    for row in cursor:
        count += 1
    return count != 0

def set_state(chat_id, state):
    
    if exists_row("temp_state", "chat_id", chat_id):
        in_table_in_row_in_col_set_val("dbo.temp_state", "chat_id", chat_id, "state_id", int(state))
    else:
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'INSERT INTO dbo.temp_state(chat_id, state_id) values ({chat_id}, {state})')
        cursor.commit()
    

def landlord_set_name(chat_id, name):
    if exists_row("Houses.landlord", "id_owner", chat_id):
        in_table_in_row_in_col_set_val("Houses.landlord", "id_owner", chat_id, "name", str(name))
    else:
        date = datetime.date.today()
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'INSERT INTO Houses.landlord(id_owner, name, announcement_number, date_registration) values \
            ({chat_id}, \'{name}\', 0, \'{date}\')')
        cursor.commit()

def tenant_set_name(chat_id, name):
    if exists_row("Houses.client", "id_client", chat_id):
        in_table_in_row_in_col_set_val("Houses.client", "id_client", chat_id, "name", str(name))
    else:
        date = datetime.date.today()
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'INSERT INTO Houses.client(id_client, name) values \
            ({chat_id}, \'{name}\')')
        cursor.commit()

def delete_new_booking(chat_id):
    if exists_row("dbo.temp_booking", "id_client", int(chat_id)):
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'DELETE FROM dbo.temp_booking WHERE id_client = {chat_id}')
        cursor.commit()
    

def delete_new_announcement(chat_id):
    if exists_row("dbo.temp_announcement", "id_owner", int(chat_id)):
        cursor = pyodbc.connect(config.connection_string).cursor()
        cursor.execute(f'DELETE FROM dbo.temp_announcement WHERE id_owner = {chat_id}')
        cursor.commit()
    
    
def exists_new_announcement(chat_id):
    return exists_row("dbo.temp_announcement", "id_owner", int(chat_id))
    
def set_new_announcement(chat_id):
    if exists_new_announcement(chat_id):
        delete_new_announcement(chat_id)
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'INSERT INTO dbo.temp_announcement(id_owner, text_description, min_nights, max_nights, pledge,\
        cost_per_night, type_house, square, latitude, longitude) values ({chat_id}, \'\', 0, 0, 0, 0, \'\', 0, 0, 0)')
    cursor.commit()
    
def set_new_announcement_description(chat_id, description):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "text_description", str(description))
    
def set_new_announcement_pledge(chat_id, pledge):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "pledge", int(pledge))
    
def set_new_announcement_square(chat_id, square):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "square", float(square))
    
def set_new_announcement_min_night(chat_id, min_night):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "min_nights", int(min_night))
    
def set_new_announcement_max_night(chat_id, max_night):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "max_nights", int(max_night))
    
def set_new_announcement_city(chat_id, city):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT id_city FROM Houses.city WHERE name = \'{city}\'')
    id_city = 0
    for row in cursor:
        id_city = row[0]
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "id_city", int(id_city))

def set_new_announcement_suburb(chat_id, suburb):
    cursor = pyodbc.connect(config.connection_string).cursor()
    cursor.execute(f'SELECT id_suburb FROM Houses.suburb WHERE name = \'{suburb}\'')
    id_suburb = 0
    for row in cursor:
        id_suburb = row[0]
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "id_suburb", int(id_suburb))
    
def set_new_announcement_latitude(chat_id, latitude):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "latitude", float(latitude))
    
def set_new_announcement_longitude(chat_id, longitude):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "longitude", float(longitude))
    
def set_new_announcement_type(chat_id, type_house):
    in_table_in_row_in_col_set_val("dbo.temp_announcement", "id_owner", chat_id, "type_house", str(type_house))
    

