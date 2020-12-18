bot = telebot.TeleBot(config.token)



def is_ok(message):
    return message == "OK" or message == "ОК"

def check_landlord(chat_id):
    return db.exists_row("Houses.landlord", "id_owner", int(chat_id))

def check_tenant(chat_id):
    return db.exists_row("Houses.client", "id_client", int(chat_id))


@bot.message_handler(commands=['start'])
def start_message(message):
    start_mes = """Привет! Это телеграм-бот для сдачи и аренды домов/квартир/комнат. Ты можешь быть как и арендодателем, так и съёмщиком."""
    bot.send_message(message.chat.id, start_mes)
    help_message(message)
    
    
    
@bot.message_handler(commands=['help'])
def help_message(message):
    help_mes = """Чтобы зарегистрироваться как арендодатель - используйте команду /reg_landloard\n
    Чтобы зарегстрироваться как арендатель - используйте команду /reg_tenant\n
    Чтобы дать объявление о сдаче помещения - используйте команду /new_announcement\n
    Чтобы найти какое-то помещение в городе - используйте команду /get_announcement\n
    Чтобы найти какое-то помещение по его id - используйте команду /get_by_id\n
    Чтобы забронировать какое-то помещение - используйте команду /booking\n
    Чтобы сделать решение насчёт какой-то брони - используйте команду /decide_booking\n"""
    bot.send_message(message.chat.id, help_mes)
    
    
@bot.message_handler(commands=['reg_landloard'])
def landlord_reg(message):
    if len(message.text) > 20:
        bot.send_message(message.chat.id, "Ваше имя должно быть короче 20-ти символов. Повторите процесс регистрации")
    bot.send_message(message.chat.id, "Если ты хочешь зарегистрировать себя в качестве арендодателя, отправь ОК\
        (в дальнешем вы сможете зарегистрироваться как арендатель)")
    db.set_state(message.chat.id, config.States.LANDLORD_ENTER_OK.value[0])

    
@bot.message_handler(commands=['change_landlord_nick'])
def landlord_enter_name(message):
    db.landlord_set_name(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Ок, вы успешно зарегистрированы!")
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    
    
@bot.message_handler(commands=['reg_tenant'])
def tenant_reg(message):
    if len(message.text) > 20:
        bot.send_message(message.chat.id, "Ваше имя должно быть короче 20-ти символов. Повторите процесс регистрации")
    bot.send_message(message.chat.id, "Если ты хочешь зарегистрировать себя в качестве арндодателя, отправь ОК\
        (в дальнешем вы сможете зарегистрироваться как аренодатель)")
    db.set_state(message.chat.id, config.States.TENANT_ENTER_OK.value[0])

    
@bot.message_handler(commands=['change_tenant_nick'])
def tenant_enter_name(message):
    db.tenant_set_name(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Ок, вы успешно зарегистрированы!")
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    

@bot.message_handler(commands=['new_announcement'])
def new_announcement(message):
    if not check_landlord(message.chat.id):
        bot.send_message(message.chat.id, "На данный момент вы не зарегистрированы как арендодатель. Сделайте это с помощью команды\n\
        /reg_landloard")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    bot.send_message(message.chat.id, "Если вы действительно хотите дать новое объявление, отправьте ОК.\
        Понадобится такая информация:\nОписание\nМинимальное кол-во ночей\nМаксимальное кол-во ночей\nЗалог\n\
        Цена за ночь\nТип\nПлощадь\nКоординаты(ширина и долгота)\nГород\nРайон")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_OK.value[0])
    db.delete_new_announcement(message.chat.id)
    

@bot.message_handler(commands=['begin_announcement'])
def begin_announcement(message):
    towns_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    towns = sorted(db.from_table_get_all_values_of_col("Houses.city", "name"))
    towns.append("Отмена")
    
    for town in towns:
        towns_kb.add(types.KeyboardButton(town))
        
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_CITY.value[0])
    db.set_new_announcement(message.chat.id)
    bot.send_message(message.chat.id, "ОК, давайте выберем город, в котором вы хотите сдавать квартиру.\
        Если вашего города нет в списке, нам очень печально, но вы не сможете сдать квартиру :( Нажать отмену вы можете снизу",
                    reply_markup=towns_kb)
    

    
@bot.message_handler(commands=['set_city'])
def set_new_announcement_city(message):
    city = sorted(db.from_table_get_all_values_of_col("Houses.city", "name"))
    if message.text not in city:
        if message.text == "Отмена":
            db.set_state(message.chat.id, config.States.NOTHING.value[0])
        else:
            bot.send_message(message.chat.id, "Мы не знаем такого города :( повторите попытку создания объявления")
    
    db.set_new_announcement_city(message.chat.id, message.text)
    
    bot.send_message(message.chat.id, "Хорошо, теперь введите описание вашей квартиры (до 1000 символов)")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_DESCRIPTION.value[0])
    
    
@bot.message_handler(commands=['set_description'])
def set_new_announcement_description(message):
    if len(message.text) > 1000:
        bot.send_message(message.chat.id, "Ваше описание слишком длинное, введите пожалуйста описание до 1000 символов")
        return
    db.set_new_announcement_description(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Хорошо, теперь введите сколько залога нужно заплатить за проживание (Число. Если залог не нужен, введите 0)")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_PLEDGE.value[0])
    
    
@bot.message_handler(commands=['set_pledge'])
def set_new_announcement_pledge(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введите, пожалуйста, число")
        return
    db.set_new_announcement_pledge(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Хорошо, теперь введите площадь квариты (Число)")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_SQUARE.value[0])
    

@bot.message_handler(commands=['set_square'])
def set_new_announcement_square(message):
    square = 0
    try:
        square = float(message.text)
    except:
        bot.send_message(message.chat.id, "Введите, пожалуйста, число")
        return
    db.set_new_announcement_square(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Хорошо, теперь введите минимальное число ночей для съёма (число)")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_MIN_NIGHT.value[0])

    
@bot.message_handler(commands=['set_min_night'])
def set_new_announcement_min_night(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введите, пожалуйста, число")
        return
    db.set_new_announcement_min_night(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Хорошо, теперь введите максимальное число ночей для съёма (число)")
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_MAX_NIGHT.value[0])
    
    
@bot.message_handler(commands=['set_max_night'])
def set_new_announcement_max_night(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введите, пожалуйста, число")
        return
    
    suburbs = sorted(db.from_table_get_all_values_of_col("Houses.suburb", "name"))
    suburbs.append('Нет моего района')
    suburbs_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    for suburb in suburbs:
        suburbs_kb.add(types.KeyboardButton(suburb))
    bot.send_message(message.chat.id, text="Хорошо, теперь выберите район, в котором находится ваша квартира \
        (если вашего района нет в списке - последний вариант)", reply_markup=suburbs_kb)
    
    
        
    db.set_state(message.chat.id, config.States.NEW_ANNOUNMENT_SUBURB.value[0])
    db.set_new_announcement_max_night(message.chat.id, message.text)
    
@bot.message_handler(commands=['set_suburb'])
def set_new_announment_suburb(message):
    suburbs = sorted(db.from_table_get_all_values_of_col("Houses.suburb", "name"))
    suburb = message.text
    if suburb not in suburbs:
        if suburbs != 'Нет моего района':
            suburbs = sorted(['Ленинский район'])
            suburbs.append('Нет моего района')
            suburbs_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
            for suburb in suburbs:
                towns_kb.add(types.KeyboardButton(suburbs))
            bot.send_message(message.chat.id, 'Пожалуйста, выберите район', reply_markup=suburbs_kb)
        else:
            suburb = ""
    db.set_new_announcement_suburb(message.chat.id, suburb)
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_LATITUDE.value[0])
    bot.send_message(message.chat.id, "Укажите широту сдаваемого помещения (десятичная дробь)")
            
        
@bot.message_handler(commands=['set_latitude'])
def set_new_announcement_latitude(message):
    latitude = 0
    try:
        latitude = float(message.text)
    except:
        bot.send_message(message.chat.id, "Введите, пожалуйста, десятичную дробь")
    db.set_new_announcement_latitude(message.chat.id, latitude)
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_LONGITUDE.value[0])
    bot.send_message(message.chat.id, "Укажите долготу сдаваемого помещения (десятичная дробь)")
        
        
        
@bot.message_handler(commands=['set_longitude'])
def set_new_announcement_longitude(message):
    longitude = 0
    try:
        longitude = float(message.text)
    except:
        bot.send_message(message.chat.id, "Введите, пожалуйста, десятичную дробь")
    db.set_new_announcement_longitude(message.chat.id, longitude)
    db.set_state(message.chat.id, config.States.NEW_ANNOUNCEMENT_TYPE.value[0])
    bot.send_message(message.chat.id, "Введите тип помещения (квартира/лофт/лодка и тому подобное)")
        

@bot.message_handler(commands=['set_type'])
def set_new_announcement_type(message):
    if len(message.text) > 30:
        bot.send_message(message.chat.id, "Введите, пожалуйста, тип до 30-ти символов")
    db.set_new_announcement_type(message.chat.id, message.text)
    db.copy_to_announcement_from_temp(message.chat.id)
    bot.send_message(message.chat.id, "Отлично! Вы создали объявление!")
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    
@bot.message_handler(commands=['get_by_id'])
def get_id_of_announcements(message):
    if not check_tenant(message.chat.id):
        bot.send_message(message.chat.id, "На данный момент вы не зарегистрированы как арендатель. Сделайте это с помощью команды\n\
        /reg_tenant")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    bot.send_message(message.chat.id, "get_id_of_announcements")
    bot.send_message(message.chat.id, 'Введите id объявления, которое вы хотите посмотреть')
    db.set_state(message.chat.id, config.States.GET_ANNOUNCEMENT_ID.value[0])
    
@bot.message_handler(commands=['get_announcements_by_id'])
def get_announcements_by_id(message):
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    try:
        id_post = int(message.text)
    except:
        bot.send_message(message.chat.id, 'Вводите в будущем id (Число)')
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
    if db.exists_row("Houses.announcement", "id_post", id_post):
        data = db.get_announcement_by_id(id_post)
    else:
        bot.send_message(message.chat.id, 'Объявления с таким id не существует, либо сейчас не актуально')
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 
    
    city = db.from_table_in_row_get_val('Houses.city', 'id_city', data[15], 'name')
    suburb = db.from_table_in_row_get_val('Houses.suburb', 'id_suburb', data[14], 'name')
    ann = f"""id объявления: {data[0]}\n
    Описание объявления: {data[1]}\n
    Средний рейтинг: {data[2]}\n
    Кол-во отзывов: {data[3]}\n
    Минимальное кол-во ночей для съёма: {data[4]}\n
    Максимальное кол-во ночей для съёма: {data[5]}\n
    Залог: {data[6]}\n
    Стоимость за одну ночь: {data[7]}
    Тип помещения: {data[8]}\n
    Площадь: {data[9]}\n
    Ширина: {data[10]}\n
    Долгота: {data[11]}\n
    Город: {city}\n
    Район: {suburb}\n
    """
    bot.send_message(message.chat.id, ann)
    
@bot.message_handler(commands=['get_announcement'])
def get_announcement(message):
    if not check_tenant(message.chat.id):
        bot.send_message(message.chat.id, "На данный момент вы не зарегистрированы как арендатель. Сделайте это с помощью команды\n\
        /reg_tenant")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    towns_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    towns = sorted(db.from_table_get_all_values_of_col("Houses.city", "name"))
    
    for town in towns:
        towns_kb.add(types.KeyboardButton(town))
        
    db.set_state(message.chat.id, config.States.SEND_ANNOUNCEMENT.value[0])
    db.set_new_announcement(message.chat.id)
    bot.send_message(message.chat.id, "Выберите город, в котором хотите найти квартиру",
                    reply_markup=towns_kb)
    
    
@bot.message_handler(commands=['send_announcement'])
def send_announcement(message):
    id_city = db.get_city_id(message.text)
    if id_city is None:
        bot.send_message(message.chat.id, "Такой город наш бот не поддерживает")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
    ids_announcements = db.get_id_with_city(id_city)
    message.text = str(ids_announcements[rand(0, len(ids_announcements) - 1)])
    get_announcements_by_id(message)
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    
@bot.message_handler(commands=['booking'])
def new_booking(message):
    if not check_tenant(message.chat.id):
        bot.send_message(message.chat.id, "На данный момент вы не зарегистрированы как арендатель. Сделайте это с помощью команды\n\
        /reg_tenant")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    db.delete_new_booking(message.chat.id)
    bot.send_message(message.chat.id, "Чтобы забронировать какое-то помещение, отошлите следующим сообщением его id")
    db.set_state(message.chat.id, config.States.BOOKING_GET_ID.value[0])
    
    
@bot.message_handler(commands=['set_id_booking'])
def set_id_booking(message):
    id_post = 0
    try:
        id_post = int(message.text)
    except:
        bot.send_message(message.chat.id, "Нужно вводить число. Повторите процесс бронирования заново")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
    if not db.exists_announcement(id_post):
        bot.send_message(message.chat.id, "Такого объявления либо нет, либо владелец снял его с рассмотрения")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
    bot.send_message(message.chat.id, "Введите дату заезда в формате yyyy-mm-dd")
    db.set_new_booking(id_post, message.chat.id)
    db.set_state(message.chat.id, config.States.BOOKING_GET_START_BOOKING.value[0])
    
@bot.message_handler(commands=['start_date'])
def set_start_date(message):
    try:
        date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
    except:
        bot.send_message(message.chat.id, "Пожалуйста, вводите дату в формате yyyy-mm-dd")
        return
    db.set_start_date(message.chat.id, date)
    db.set_state(message.chat.id, config.States.BOOKING_GET_END_BOOKING.value[0])
    bot.send_message(message.chat.id, "Введите дату заезда в формате yyyy-mm-dd")
    
@bot.message_handler(commands=['end_date'])
def set_end_date(message):
    try:
        date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
    except:
        bot.send_message(message.chat.id, "Пожалуйста, вводите дату в формате yyyy-mm-dd")
        return
    db.set_end_date(message.chat.id, date)
    db.set_state(message.chat.id, config.States.NOTHING.value[0])
    id_owner, id_post, start_date, end_date, id_booking = db.copy_to_booking_from_temp(message.chat.id)
    bot.send_message(message.chat.id, f"Ваша заявка успешно оставлена, номер брони {id_booking}")
    bot.send_message(id_owner, f"Обратились по вашему объявлению {id_post}\n\
    Хотят снять с {start_date} по {end_date}\n\
    Номер брони {id_booking}\n\
    Для отказа или согласования воспользуйтесь командой /decide_booking\n")
    
    
@bot.message_handler(commands=['decide_booking'])
def decide_booking(message):
    if not check_landlord(message.chat.id):
        bot.send_message(message.chat.id, "На данный момент вы не зарегистрированы как арендодатель. Сделайте это с помощью команды\n\
        /reg_landloard")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    bot.send_message(message.chat.id, "Пришлите номер бронирования")
    db.set_state(message.chat.id, config.States.LANDLORD_GET_BOOKING_ID.value[0])
    
@bot.message_handler(commands=['decision_booking'])
def decision_booking(message):
    id_booking = 0
    try:
        id_booking = int(message.text)
    except:
        bot.send_message(message.chat.id, "Повторите попытку заново. Вводите число")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
        
    if not db.check_booking(message.chat.id, id_booking):
        bot.send_message(message.chat.id, "У вас нет такой брони, повторите попытку заново")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return
        
    decisions_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    decisions_kb.add(types.KeyboardButton("Одобрить"))
    decisions_kb.add(types.KeyboardButton("Отклонить"))
    db.new_decision(message.chat.id, id_booking)
    bot.send_message(message.chat.id, text="Для принятия решения нажмите на одну из кнопок", reply_markup=decisions_kb)
    db.set_state(message.chat.id, config.States.MAKE_DECISION.value[0])
    
@bot.message_handler(commands=['make_decision'])
def make_decision(message):
    if message.text not in ['Одобрить', 'Отклонить']:
        bot.send_message(message.chat.id, "Ваше решение не было понятно. Для принятия решения нажимайте на одну из выпадающих кнопок\n\
        Повторите процесс решения брони")
        db.set_state(message.chat.id, config.States.NOTHING.value[0])
        return 0
    if message.text == 'Одобрить':
        dec = 1
    else:
        dec = 2
    id_client, id_booking = db.make_decision(message.chat.id, dec)
    bot.send_message(message.chat.id, "Ваше решение принятно!")
    if dec == 1:
        bot.send_message(id_client, f"Ваша бронь {id_booking} успешно одобрена. Ждём вас на месте!")
    else:
        bot.send_message(id_client, f"Ваша брони {id_booking} отклонена.")
    
    
@bot.message_handler(content_types=['text'])
def msg_handler(message):
    state = db.get_state(message.chat.id)
    if state == config.States.LANDLORD_ENTER_OK.value[0]:
        if is_ok(message.text):
            bot.send_message(message.chat.id, "Введите ваше имя")
            db.set_state(message.chat.id, config.States.LANDLORD_ENTER_NAME.value[0])
        else:
            db.set_state(message.chat.id, config.States.NOTHING.value[0])
        
    elif state == config.States.LANDLORD_ENTER_NAME.value[0]:
        landlord_enter_name(message)
        
    elif state == config.States.TENANT_ENTER_OK.value[0] and is_ok(message.text):
        if is_ok(message.text):
            bot.send_message(message.chat.id, "Введите ваше имя")
            db.set_state(message.chat.id, config.States.TENANT_ENTER_NAME.value[0])
        else:
            db.set_state(message.chat.id, config.States.NOTHING.value[0])

    elif state == config.States.TENANT_ENTER_NAME.value[0]:
        tenant_enter_name(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_OK.value[0]:
        if is_ok(message.text):
            begin_announcement(message)
        else:
            db.set_state(message.chat.id, config.States.NOTHING.value[0])

    elif state == config.States.NEW_ANNOUNCEMENT_CITY.value[0]:
        set_new_announcement_city(message)

    elif state == config.States.NEW_ANNOUNCEMENT_DESCRIPTION.value[0]:
        set_new_announcement_description(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_PLEDGE.value[0]:
        set_new_announcement_pledge(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_SQUARE.value[0]:
        set_new_announcement_square(message)
    
    elif state == config.States.NEW_ANNOUNCEMENT_MIN_NIGHT.value[0]:
        set_new_announcement_min_night(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_MAX_NIGHT.value[0]:
        set_new_announcement_max_night(message)
    
    elif state == config.States.NEW_ANNOUNMENT_SUBURB.value[0]:
        set_new_announment_suburb(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_LATITUDE.value[0]:
        set_new_announcement_latitude(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_LONGITUDE.value[0]:
        set_new_announcement_longitude(message)
        
    elif state == config.States.NEW_ANNOUNCEMENT_TYPE.value[0]:
        set_new_announcement_type(message)
        
    elif state == config.States.GET_ANNOUNCEMENT_ID.value[0]:
        get_announcements_by_id(message)
    
    elif state == config.States.SEND_ANNOUNCEMENT.value[0]:
        send_announcement(message)
    
    elif state == config.States.BOOKING_GET_ID.value[0]:
        set_id_booking(message)
    
    elif state == config.States.BOOKING_GET_START_BOOKING.value[0]:
        set_start_date(message)
    
    elif state == config.States.BOOKING_GET_END_BOOKING.value[0]:
        set_end_date(message)
    
    elif state == config.States.LANDLORD_GET_BOOKING_ID.value[0]:
        decision_booking(message)
    
    elif state == config.States.MAKE_DECISION.value[0]:
        make_decision(message)
        
    
bot.polling()
