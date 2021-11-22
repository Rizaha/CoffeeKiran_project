from loguru import logger
import psycopg2
from flask import Flask
from flask import request as rq
from flask import jsonify
from werkzeug.exceptions import Unauthorized
import coffeeKiran_function as func

def connect():
    koneksi = psycopg2.connect(user="postgres",
                               password="admin",
                               host="127.0.0.1",
                               port="5432",
                               database="cofee_shop")
    return koneksi

def login():
    username = rq.authorization["username"]
    password = rq.authorization["password"]

    connection = connect()
    cursor = connection.cursor()

    query = "select id, username, password from users where username=%s"
    cursor.execute(query, (username,),)
    user = cursor.fetchone()
    # logger.debug(user[2])
    if user is None or password != user[2]:
        raise Unauthorized()

    else :
        # query2 = "UPDATE public.users\
        #             SET last_login_at=NOW()\
        #             WHERE username = %s;"
        # cursor.execute(query2, (username,),)
        # connection.commit()
        return True

def isadmin():
    username = rq.authorization["username"]
    password = rq.authorization["password"]

    connection = connect()
    cursor = connection.cursor()

    query = "select is_admin from users where username=%s"
    cursor.execute(query, (username,),)
    user = cursor.fetchone()
    logger.debug(user[0])

    if user is None or user[0] != True:
        raise Unauthorized()

    else :
        return True


app = Flask(__name__)

@app.route('/coffeekiran/signup', methods=['POST'])
def signup():
    connection = connect()
    cursor = connection.cursor()
    data = rq.json

    mail = data["email"]
    uname = data["username"]
    pasw = data["password"]

    # logger.debug(func.f_email(uname))
    # logger.debug(mail)
    postgreSQL_select_Query = "INSERT INTO public.users(\
	                            username, email, password)\
	                            VALUES (%s, %s, %s);"
    try:
        cursor.execute(postgreSQL_select_Query, (uname, mail, pasw))
        connection.commit()
        return jsonify({
            'message' : 'Selamat datang di Coffee Kiran, silahkan lihat tutorial pemesanan',
            'tutorial_langkah1' : 'ambil antrian di .... ',
            'tutorial_langkah2' : 'lihat menu di .... ',
            'tutorial_langkah3' : 'pesan di .... ',
            'tutorial_langkah4' : 'hapus pesanan di ...',
            'tutorial_langkah5' : 'tambah pesanan di ... ',
            'tutorial_langkah6' : 'cek pesanan di ...',
            'tutorial_langkah7' : 'upadte user di ...'
        }), 201
    except:
        return jsonify({
            'error' : 'bad request',
            'message' : 'username atau email sudah terdaftar'
        }), 400


@app.route('/coffeekiran/user/update-user', methods=['PUT'])
def update_user():
    if not login():
        return "gagal login", 401
    else:
        connection = connect()
        cursor = connection.cursor()
        data = rq.json

        mail = data["email"]
        uname = data["username"]
        pasw = data["password"]
        
        username = rq.authorization["username"]

        postgreSQL_select_Query = "UPDATE public.users\
	                                SET username=%s, email=%s, password=%s\
	                                WHERE username = %s;"
        try:
            cursor.execute(postgreSQL_select_Query,(uname,mail,pasw,username))
            connection.commit()

            return jsonify({
                'report' : 'success',
                'message' : 'username sudah terupdate !'
            }), 400

        except:
            return jsonify({
                'error' : 'bad request',
                'message' : 'username atau email sudah terdaftar'
            }), 400


@app.route('/coffeekiran/admin/addmenu', methods=['POST'])
def addmenu():
    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    else:
        connection = connect()
        cursor = connection.cursor()
        data = rq.json

        name = data["nama"]
        deskripsi = data["deskripsi"]
        stock = data["stok"]
        price = data["harga"]
        logger.debug(price)
        postgreSQL_select_Query = "INSERT INTO public.menus(\
                            name, stock, description, price)\
                            VALUES (%s, %s, %s, %s);"

        try:
            a = cursor.execute(postgreSQL_select_Query,(name,stock,deskripsi,price))
            logger.debug(a)
            connection.commit()

            return jsonify({
                'report' : 'success',
                'message' : 'menu sudah ditambahkan !'
            }), 201

        except:
            return jsonify({
                'error' : 'bad request',
                'message' : 'nama atau deskripsi sudah terdaftar'
            }), 400


@app.route('/coffeekiran/admin/update-data-menu', methods=['PUT'])
def update_data_menu():
    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    else:
        connection = connect()
        cursor = connection.cursor()
        data = rq.json

        menu_id = data["menu_id"]
        name = data["nama"]
        deskripsi = data["deskripsi"]
        price = data["harga"]

        postgreSQL_select_Query = "UPDATE public.menus\
	                                SET name=%s, description=%s, price=%s\
	                                WHERE id = %s;"
        try:
            a = cursor.execute(postgreSQL_select_Query,(name,deskripsi,price,menu_id))
            connection.commit()
            if a == None:
                return "ID menu tidak ditemukan", 400
            else :
                return jsonify({
                    'report' : 'success',
                    'message' : 'menu sudah terupdate !'
                }), 201

        except:
            return jsonify({
                'error' : 'bad request',
                'message' : 'menu atau deskripsi sudah terdaftar'
            }), 400


@app.route('/coffeekiran/admin/update-stock', methods=['PUT'])
def update_stok():
    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    else:
        connection = connect()
        cursor = connection.cursor()
        data = rq.json

        menu_id = data["menu_id"]
        stock = data["stock"]

        postgreSQL_select_Query = "UPDATE public.menus\
	                                SET stock=%s\
	                                WHERE id = %s;"
        a = cursor.execute(postgreSQL_select_Query,(stock,menu_id))
        connection.commit()
        
        if a == None:
            return "ID menu tidak ditemukan", 400
        else:
            return jsonify({
                'report' : 'success',
                'message' : 'stock sudah terupdate !'
            }), 201


@app.route('/coffeekiran/admin/cek-pesanan', methods=['GET'])
def cek_pesanan():
    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    else:
        arr=[]
        connection = connect()
        cursor = connection.cursor()

        postgreSQL_select_Query = "select  u.username, ol.order_id, o.menu_id, o.jumlah, ol.is_complete\
                                from order_lists as ol\
                                join orders as o\
                                on ol.order_id = o.order_id\
                                join users as u\
                                on u.id=ol.user_id\
                                where ol.is_complete = false\
                                order by order_at"
        cursor.execute(postgreSQL_select_Query)
        orders = cursor.fetchall()
        for row in orders:
            arr.append({
                "1_Username": str(row[0]),
                "2_oerderID" : str(row[1]),
                "3_menuID": str(row[2]),
                "4_jumlah": str(row[3]),
                "5_isComplete": str(row[4])
            })
        return jsonify(arr)


@app.route('/coffeekiran/admin/ceklis-pesanan', methods=['PUT'])
def ceklis_pesanan():
    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    else:
        connection = connect()
        cursor = connection.cursor()

        order_id = rq.args.get('orderID')

        postgreSQL_select_Query = "UPDATE public.order_lists\
	                                SET is_complete=%s\
	                                WHERE order_id = %s;"
        cursor.execute(postgreSQL_select_Query,(True,order_id))
        connection.commit()

        return f'order ke{order_id} sudah selesai'


@app.route('/coffeekiran/menu', methods=['GET'])
def list_menu():
    arr=[]
    connection = connect()
    cursor = connection.cursor()

    postgreSQL_select_Query = "select name, id, stock, description, price\
                                from menus\
                                order by added_at"

    cursor.execute(postgreSQL_select_Query)
    menus = cursor.fetchall()
    for row in menus:
            arr.append({
                "1_Nama": str(row[0]),
                "2_id" : str(row[1]),
                "3_Stok": str(row[2]),
                "4_Deskripsi": str(row[3]),
                "5_Harga": str(row[4])
            })
    return jsonify(arr)


@app.route('/coffeekiran/user/ambil-antrian', methods=['GET'])
def antrian():
    if not login():
        return "gagal login", 401
    else:
        connection = connect()
        cursor = connection.cursor()
        username = rq.authorization["username"]
        id = func.user_id(username)
        logger.debug(id)
        postgreSQL_select_Query = "INSERT INTO public.order_lists(\
	                                user_id)\
	                                VALUES (%s);"

        cursor.execute(postgreSQL_select_Query,(id,),)
        connection.commit()

        Query_antrianID= "select order_id from order_lists where user_id = (select id from users where username = %s) order by order_id desc"
        cursor.execute(Query_antrianID,(username,),)

        a =cursor.fetchone()
        return jsonify({
            'nomor_antrian' : a
        }), 201


@app.route('/coffeekiran/user/pesan', methods=['POST'])
def pesan():
    connection = connect()
    cursor = connection.cursor()

    data = rq.json
    antrian = rq.args.get('no_antrian')
    if not login():
        return "gagal login", 401

    else:
        menu_id = data["menu_id"]
        jumlah = data["jumlah"]

        username = rq.authorization["username"]
        
        if antrian == None:
            return "harap masukan nomor antrian"
        logger.debug(func.user_id(username))
        logger.debug(func.select_user(antrian))
        if str(func.user_id(username)) != str(func.select_user(antrian)):
            return "cek nomor antrian", 400

        if func.antrian_count() > 10:
            return jsonify({
                'error' : 'bad request',
                'message' : 'pegawai sedang sibuk'
            }), 400

        if (func.stock(menu_id)[0]== None) or ((int(data["jumlah"]) > func.stock(menu_id)[0])):
            return jsonify({
                'error' : 'bad request',
                'message' : 'menu out of stock, harap cek stok'
            }), 400

        else :
            postgreSQL_select_Query = "INSERT INTO public.orders(\
	                                user_id, menu_id, jumlah, order_id)\
	                                VALUES (%s, %s, %s, %s);"
            cursor.execute(postgreSQL_select_Query, (str(func.user_id(username)), menu_id, jumlah, antrian))
            connection.commit()
            # logger.debug(func.menu(menu_id))
            # logger.debug(func.totalHarga(antrian)*jumlah)

            query = 'UPDATE public.menus\
			        SET  stock = ((select stock from menus where id = %s)-%s)\
			        WHERE id=%s;'
            cursor.execute(query,(menu_id,jumlah,menu_id))
            connection.commit()
            
            return jsonify({
                    "antiran": antrian,
                    "username" : username,
                    "menu": func.menu(menu_id),
                    "total_harga": str(func.totalHarga(menu_id,jumlah,antrian))
                })


@app.route('/coffeekiran/user/cancel-pesanan', methods=['DELETE'])
def cancel():
    connection = connect()
    cursor = connection.cursor()

    antrian = rq.args.get('no_antrian')
    if not login():
        return "gagal login", 401

    else:
        username = rq.authorization["username"]
        antrian = rq.args.get('no_antrian')
        # logger.debug(str(func.select_user(antrian)))
        # logger.debug(antrian)
        if antrian == None:
            return "harap masukan nomor antrian"

        if str(func.user_id(username)) != str(func.select_user(antrian)):
            return "cek nomor antrian", 400
        
        # logger.debug((int(antrian),))
        # logger.debug(func.semua_antrian())
        if (int(antrian),) in func.order_selesai():
            return "order tidak bisa dicancel karena sudah selesai dibuat", 400

        if (int(antrian),) not in func.semua_antrian():
            return "antrian tidak ditemukan", 400
        
        else:
            logger.debug(func.select_menu_order(antrian))
            logger.debug(func.select_jumlah(antrian))

            for i in func.select_menu_order(antrian):
                for j in func.select_jumlah(antrian):
                    postgreSQL_select_Query = "UPDATE public.menus\
                                                SET stock=(select stock from menus where id = %s) + %s\
                                                WHERE id=%s;"
                    cursor.execute(postgreSQL_select_Query, (i,j,i))
                    connection.commit()
                    break

            postgreSQL_select_Query = "UPDATE public.order_lists\
                                    SET is_complete = null\
                                    WHERE order_id = %s;"
            cursor.execute(postgreSQL_select_Query, (antrian,),)
            connection.commit()
            return "order canceled", 201


@app.route('/coffeekiran/user/lihat-pesanan', methods=['GET'])
def cek_pesanan_user():
    connection = connect()
    cursor = connection.cursor()

    antrian = rq.args.get('no_antrian')
    if not login():
        return "gagal login", 401

    else:
        arr=[]
        username = rq.authorization["username"]
        # logger.debug(func.antrian_count())
        if antrian == None:
            return "harap masukan nomor antrian"

        if str(func.user_id(username)) != str(func.select_user(antrian)):
            return "cek nomor antrian", 400

        else :
            postgreSQL_select_Query = "select o.user_id, m.id, m.name, o.jumlah\
                                        from order_lists as ol\
                                        join orders as o\
                                        on ol.user_id=o.user_id\
                                        join menus as m\
                                        on m.id = o.menu_id\
                                        where ol.order_id = %s"
            cursor.execute(postgreSQL_select_Query,(antrian,),)
            orders=cursor.fetchall()
            for row in orders:
                arr.append({
                    "user_id": str(row[0]),
                    "menu_id" : str(row[1]),
                    "menu_nama": str(row[2]),
                    "jumlah": str(row[3])
                })
        return jsonify(arr)


@app.route('/coffeekiran/user/update-pesanan', methods=['PUT'])
def update_pesanan():
    connection = connect()
    cursor = connection.cursor()

    data = rq.json
    
    menu_id = data["menu_id"]
    jumlah = data["jumlah"]
    if not login():
        return "gagal login", 401

    else:
        username = rq.authorization["username"]
        antrian = rq.args.get('no_antrian')
        # logger.debug(str(func.select_user(antrian)))
        # logger.debug(str(func.user_id(username)))
        if antrian == None:
            return "harap masukan nomor antrian"

        if str(func.user_id(username)) != str(func.select_user(antrian)):
            return "cek nomor antrian", 400
        
        # logger.debug((int(antrian),))
        logger.debug(func.select_jumlah_menu(antrian,menu_id))
        if (int(antrian),) in func.order_selesai():
            return "order tidak bisa diupdate karena sudah selesai dibuat", 400

        if (int(antrian),) not in func.semua_antrian():
            return "antrian tidak ditemukan", 400

        else:
            query = 'UPDATE public.menus\
			        SET  stock = ((select stock from menus where id = %s)+%s-%s)\
			        WHERE id=%s;'
            cursor.execute(query,(menu_id,str(func.select_jumlah_menu(antrian,menu_id)),jumlah,menu_id))
            connection.commit()
            

            postgreSQL_select_Query = "UPDATE public.orders\
	                                    SET  menu_id=%s, jumlah=%s\
	                                    WHERE order_id=%s and menu_id=%s;"
            cursor.execute(postgreSQL_select_Query, (menu_id,jumlah,antrian,menu_id))
            connection.commit()

            return jsonify({
                    "success": "update selesai",
                    "message" : "harap cek pesanan lagi"
                })


@app.route('/coffeekiran/search', methods=['GET'])
def search_menu():
    arr = []
    menu = rq.args.get('menu')
    logger.debug(menu)

    connection = connect()
    cursor = connection.cursor()
    postgreSQL_select_Query = f"SELECT id, name, stock, price FROM menus WHERE name LIKE '%{menu}%'"

    cursor.execute(postgreSQL_select_Query)
    menus = cursor.fetchall()
    logger.debug(menus)
    if menus == []:
        return "Menu tidak ditemukan"
    else:
        for row in menus:
            arr.append({
                "menu_id = ": str(row[0]),
                "nama = ": str(row[1]),
                "stok = ": str(row[2]),
                "harga = " : str(row[3])
            })

        return jsonify(arr)


@app.route('/coffeekiran/top-order', methods=['GET'])
def top_order():
    arr = []
    connection3 = connect()
    cursor = connection3.cursor()
    postgreSQL_select_Query = "select ol.user_id, u.username, count(ol.order_id)\
                                from order_lists as ol\
                                join users as u\
                                on ol.user_id = u.id\
                                group by ol.user_id, u.username\
                                order by count(ol.order_id) desc\
                                limit 5"

    cursor.execute(
        postgreSQL_select_Query
    )
    user_records = cursor.fetchall()
    for row in user_records:
        arr.append({
            "user_id = ": str(row[0]),
            "username = ": str(row[1]),
            "jumlah pesanan = ": str(row[2])
        })

    return jsonify(arr)


@app.route('/coffeekiran/popular-menu', methods=['GET'])
def pop_menu():
    arr = []
    connection3 = connect()
    cursor = connection3.cursor()
    postgreSQL_select_Query = "select o.menu_id, m.name, count(o.order_id)\
                                from orders as o\
                                join menus as m\
                                on o.menu_id = m.id\
                                group by o.menu_id, m.name\
                                order by count(o.order_id) desc\
                                limit 5"

    cursor.execute(postgreSQL_select_Query)
    user_records = cursor.fetchall()
    for row in user_records:
        arr.append({
            "menu_id = ": str(row[0]),
            "menu_name = ": str(row[1]),
            "total pesanan = ": str(row[2])
        })

    return jsonify(arr)


if __name__ == '__main__':
    app.run(debug=True)