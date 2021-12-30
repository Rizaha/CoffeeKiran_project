import coffeeKiran_app as app

def f_username(username):
	try:
		connection = app.connect()
		cursor = connection.cursor()
		query = 'select username \
				from users\
				where username = %s'
		cursor.execute(query, (username,),)
		user = cursor.fetchone()

		return user
	except:
		return 'salah'

def f_email(email):
	try:
		connection = app.connect()
		cursor = connection.cursor()
		query = 'select email \
				from users\
				where email = %s'
		cursor.execute(query, (email,),)
		email = cursor.fetchone()

		return email
	except:
		return 'salah'

def f_password(username):
	try:
		connection = app.connect()
		cursor = connection.cursor()
		query = 'select password \
				from users\
				where username = %s'
		cursor.execute(query, (username,),)
		password = cursor.fetchone()

		return password
	except:
		return 'salah'

def stock(menu):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select stock \
			from menus\
			where id = %s'
	cursor.execute(query, (menu,),)
	menu_id = cursor.fetchone()

	return menu_id

def user_id(username):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select id \
			from users\
			where username = %s'
	cursor.execute(query, (username,))
	userid = cursor.fetchone()[0]

	return userid

def menu(menu_id):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select name \
			from menus\
			where id = %s'
	cursor.execute(query, (menu_id,),)
	menu = cursor.fetchone()[0]

	return menu

def totalHarga(menu_id,jumlah):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select (select price from menus where id =%s)*%s\
			from menus'
	cursor.execute(query, (menu_id,jumlah))
	total = cursor.fetchone()[0]

	return total

def antrian_count():
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select count(is_complete)\
			from order_lists\
			where is_complete=false'
	cursor.execute(query)
	total = cursor.fetchone()[0]

	return total

def semua_antrian():
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select order_id\
			from order_lists\
			where is_complete=false'
	cursor.execute(query)
	semuaOrder = cursor.fetchall()
  
	return semuaOrder

def order_selesai():
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select order_id\
			from order_lists\
			where is_complete = true'
	cursor.execute(query)
	semuaSelesai = cursor.fetchall()
  
	return semuaSelesai

def select_user(antrian):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select user_id\
			from order_lists\
			where order_id = %s'
	cursor.execute(query,(antrian,),)
	user_id = cursor.fetchone()[0]
  
	return user_id

def select_menu_order(user_id):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select menu_id\
			from orders\
			where user_id=%s and order_id is null'
	cursor.execute(query,(user_id,),)
	menu_id = cursor.fetchall()
  
	return menu_id

# def select_jumlah(user_id, menu_id):
# 	connection = app.connect()
# 	cursor = connection.cursor()
# 	query = 'select jumlah\
# 			from orders\
# 			where user_id=%s and menu_id=%s and order_id isnull'
# 	cursor.execute(query,(user_id, menu_id))
# 	jumlah = cursor.fetchall()
  
# 	return jumlah

def select_jumlah_menu(user_id, menu_id):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select jumlah\
			from orders\
			where user_id=%s and menu_id=%s and order_id is null'
	cursor.execute(query,(user_id,menu_id))
	jumlah = cursor.fetchone()[0]
  
	return jumlah

def daftar_menu_id():
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select id\
			from menus'
	cursor.execute(query)
	id = cursor.fetchall()
  
	return id

def cek_pesanan_masuk(user_id):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select is_complete\
			from order_lists\
			where user_id = %s'
	cursor.execute(query,(user_id,),)
	id = cursor.fetchone()[0]
  
	return id

def cek_is_confirm(antrian):
	connection = app.connect()
	cursor = connection.cursor()
	query = 'select is_confirmed\
			from order_lists\
			where order_id = %s'
	cursor.execute(query,(antrian,),)
	id = cursor.fetchone()[0]
  
	return id

def orderan(keterangan):
	if keterangan == True:
		return "Selesai"
	else:
		return "Dalam Proses"