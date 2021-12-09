from loguru import logger
import psycopg2
from flask import Flask
from flask import request as rq
from flask import jsonify
from werkzeug.exceptions import Unauthorized
import coffeeKiran_function as func
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# cors = CORS(app, resources={r"/coffeekiran/*" : {"origins":"http://127.0.0.1:5000"}})


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

@app.route('/coffeekiran/login', methods=['GET'])
def masuk():
    username = rq.authorization["username"]

    if not login():
        return "gagal login", 401
    else:
        return f'Selamat datang kak {username}'

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
            'message' : 'selamat datang di Coffee Kiran'
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
        logger.debug(menu_id)
        postgreSQL_select_Query = 'UPDATE public.menus\
	                            SET  name=%s,  description=%s, price=%s\
	                            WHERE id = %s;'
        try:
            if (int(menu_id),) not in func.daftar_menu_id():
                return "id menu tidak ditemukan", 400

            else :
                cursor.execute(postgreSQL_select_Query,(name,deskripsi,price,menu_id))
                connection.commit()
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
        stock = data["stok"]
        if (int(menu_id),) not in func.daftar_menu_id():
                return "id menu tidak ditemukan", 400
        
        else:
            postgreSQL_select_Query = "UPDATE public.menus\
	                                SET stock=%s\
	                                WHERE id = %s;"
            cursor.execute(postgreSQL_select_Query,(stock,menu_id))
            connection.commit()
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
                "username": str(row[0]),
                "order_id" : str(row[1]),
                "menu_id": str(row[2]),
                "jumlah": str(row[3]),
                "is_complete": str(row[4])
            })
        return jsonify(arr)


@app.route('/coffeekiran/admin/ceklis-pesanan', methods=['PUT'])
def ceklis_pesanan():
    order_id = rq.args.get('orderID')

    if not login() :
        return"cek admin"
    if not isadmin():
        return "anda bukan admin", 401
    if str(func.cek_is_confirm(order_id)) == str(False):
        return "user masih memesan"
    else:
        connection = connect()
        cursor = connection.cursor()

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
                "nama": str(row[0]),
                "id" : str(row[1]),
                "stok": str(row[2]),
                "deskripsi": str(row[3]),
                "harga": str(row[4])
            })
    return jsonify(arr)


# @app.route('/coffeekiran/user/ambil-antrian', methods=['GET'])
# def antrian():
#     if not login():
#         return "gagal login", 401
#     else:
#         connection = connect()
#         cursor = connection.cursor()
#         username = rq.authorization["username"]
#         id = func.user_id(username)
#         logger.debug(id)
#         postgreSQL_select_Query = "INSERT INTO public.order_lists(\
# 	                                user_id)\
# 	                                VALUES (%s);"

#         cursor.execute(postgreSQL_select_Query,(id,),)
#         connection.commit()

#         Query_antrianID= "select order_id from order_lists where user_id = (select id from users where username = %s) order by order_id desc"
#         cursor.execute(Query_antrianID,(username,),)

#         a =cursor.fetchone()
#         return jsonify({
#             'nomor_antrian' : a
#         }), 201


@app.route('/coffeekiran/user/pesan', methods=['POST'])
def pesan():
    connection = connect()
    cursor = connection.cursor()

    
    # antrian = rq.args.get('no_antrian')
    if not login():
        return "gagal login", 401

    else:
        data = rq.json
        menu_id = data["menu_id"]
        jumlah = data["jumlah"]

        username = rq.authorization["username"]
        
        # if antrian == None:
        #     return "harap masukan nomor antrian"
        # logger.debug(func.user_id(username))
        # logger.debug(func.select_user(antrian))
        # if str(func.user_id(username)) != str(func.select_user(antrian)):
        #     return "cek nomor antrian", 400

        # if func.antrian_count() > 10:
        #     return jsonify({
        #         'error' : 'bad request',
        #         'message' : 'pegawai sedang sibuk'
        #     }), 400

        logger.debug((int(menu_id),))
        logger.debug(func.daftar_menu_id())

        if (int(menu_id),) not in func.daftar_menu_id():
            return 'menu tidak ditemukan', 400

        if (func.stock(menu_id)[0]== None) or ((int(data["jumlah"]) > func.stock(menu_id)[0])):
            return jsonify({
                'error' : 'bad request',
                'message' : 'menu out of stock, harap cek stok'
            }), 400

        else :
            postgreSQL_select_Query = "INSERT INTO public.orders(\
	                                user_id, menu_id, jumlah)\
	                                VALUES (%s, %s, %s);"
            cursor.execute(postgreSQL_select_Query, (str(func.user_id(username)), menu_id, jumlah))
            connection.commit()
            # logger.debug(func.menu(menu_id))
            # logger.debug(func.totalHarga(antrian)*jumlah)

            # query = 'UPDATE public.menus\
			#         SET  stock = ((select stock from menus where id = %s)-%s)\
			#         WHERE id=%s;'
            # cursor.execute(query,(menu_id,jumlah,menu_id))
            # connection.commit()
            
            return jsonify({
                    "username" : username,
                    "menu": func.menu(menu_id),
                    "total_harga": str(func.totalHarga(menu_id,jumlah))
                })


@app.route('/coffeekiran/user/hapus-pesanan', methods=['DELETE'])
def cancel():
    connection = connect()
    cursor = connection.cursor()

    data = rq.json
    menu_id = data["menu_id"]

    if not login():
        return "gagal login", 401

    else:
        username = rq.authorization["username"]
        # antrian = rq.args.get('no_antrian')
        # logger.debug(str(func.select_user(antrian)))
        # logger.debug(antrian)
        # if antrian == None:
        #     return "harap masukan nomor antrian"

        # if str(func.user_id(username)) != str(func.select_user(antrian)):
        #     return "cek nomor antrian", 400
        
        # logger.debug((int(antrian),))
        # logger.debug(func.semua_antrian())
        # if (int(antrian),) in func.order_selesai():
        #     return "order tidak bisa dicancel karena sudah selesai dibuat", 400

        # if (int(antrian),) not in func.semua_antrian():
        #     return "antrian tidak ditemukan", 400

        # if str(func.cek_is_confirm(antrian)) == True:
        #     return f"pesanan ke-{antrian} tidak bisa dicancel, karena sudah dikonfirmasi",400
        if func.select_menu_order(str(func.user_id(username))) is None:
            return "tidak ada order", 400

        else:
            logger.debug(menu_id)
            logger.debug(str(func.user_id(username)))
            logger.debug(func.select_jumlah_menu(str(func.user_id(username)),menu_id))

            postgreSQL_select_Query = "DELETE FROM public.orders\
	                                    WHERE user_id=%s and menu_id=%s and order_id isnull;"
            cursor.execute(postgreSQL_select_Query, (str(func.user_id(username)), menu_id))
            connection.commit()
            return "order canceled", 201


@app.route('/coffeekiran/user/cek-keranjang', methods=['GET'])
def cek_pesanan_user():
    connection = connect()
    cursor = connection.cursor()

    # antrian = rq.args.get('no_antrian')
    if not login():
        return "gagal login", 401

    else:
        arr=[]
        username = rq.authorization["username"]
        # logger.debug(func.antrian_count())
        # if antrian == None:
        #     return "harap masukan nomor antrian"

        # if str(func.user_id(username)) != str(func.select_user(antrian)):
        #     return "cek nomor antrian", 400
        # logger.debug(str(func.cek_pesanan(antrian)))

        # if str(func.cek_pesanan(str(func.user_id(username)))) != str(False):
        #     return "tidak ada pesanan",200
        # else :
        postgreSQL_select_Query = "select o.user_id, m.id, m.name, o.jumlah\
                                    from orders as o\
                                    join menus as m\
                                    on m.id = o.menu_id\
                                    where o.user_id = %s and o.order_id is null"
        cursor.execute(postgreSQL_select_Query,(str(func.user_id(username)),),)
        orders=cursor.fetchall()
        if orders == []:
            return "tidak ada pesanan aktif", 400
        else:
            for row in orders:
                arr.append({
                    "user_id": str(row[0]),
                    "menu_id" : str(row[1]),
                    "menu_nama": str(row[2]),
                    "jumlah": str(row[3])
                })
            return jsonify(arr), 200


@app.route('/coffeekiran/user/update-keranjang', methods=['PUT'])
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
        # antrian = rq.args.get('no_antrian')
        # logger.debug(str(func.select_user(antrian)))
        # logger.debug(str(func.user_id(username)))
        # if antrian == None:
        #     return "harap masukan nomor antrian"

        # if str(func.user_id(username)) != str(func.select_user(antrian)):
        #     return "cek nomor antrian", 400
        # if str(func.cek_is_confirm(antrian)) == True:
        #     return "tidak bisa dipudate, sedang dibuatkan"
        # # logger.debug((int(antrian),))
        # logger.debug(func.select_jumlah_menu(antrian,menu_id))
        # if (int(antrian),) in func.order_selesai():
        #     return "order tidak bisa diupdate karena sudah selesai dibuat", 400

        # if (int(antrian),) not in func.semua_antrian():
        #     return "antrian tidak ditemukan", 400
        if (int(menu_id),) not in func.select_menu_order(str(func.user_id(username))):
            return 'menu tidak ditemukan harap pesan di menu pesan', 400
        
        else:
            query = 'UPDATE public.menus\
                    SET  stock = ((select stock from menus where id = %s)+%s-%s)\
                    WHERE id=%s;'
            cursor.execute(query,(menu_id,str(func.select_jumlah_menu(str(func.user_id(username)),menu_id)),jumlah,menu_id))
            connection.commit()
            

            postgreSQL_select_Query = "UPDATE public.orders\
                                        SET  menu_id=%s, jumlah=%s\
                                        WHERE user_id=%s and menu_id=%s and order_id is null;"
            cursor.execute(postgreSQL_select_Query, (menu_id,jumlah,str(func.user_id(username)),menu_id))
            connection.commit()

            return jsonify({
                    "success": "update selesai",
                    "message" : "harap cek pesanan lagi"
                }), 200


@app.route('/coffeekiran/user/confirm-pesanan', methods=['POST'])
def confirm():
    arr=[]
    connection = connect()
    cursor = connection.cursor()

    username = rq.authorization['username']
    postgreSQL_select_Query = "select o.user_id, m.id, m.name, o.jumlah\
                                    from orders as o\
                                    join menus as m\
                                    on m.id = o.menu_id\
                                    where o.user_id = %s and o.order_id is null"
    cursor.execute(postgreSQL_select_Query,(str(func.user_id(username)),),)
    orders=cursor.fetchall()
    if orders == []:
        return "tidak ada pesanan aktif",400
    else:
        for i in func.select_menu_order(str(func.user_id(username))):
            postgreSQL_select_Query = "UPDATE public.menus\
                                        SET stock=(select stock from menus where id=%s)-(select jumlah from orders where user_id=%s and menu_id=%s and order_id isnull)\
                                        WHERE id=%s;"
            cursor.execute(postgreSQL_select_Query, (i,str(func.user_id(username)),i,i))
            connection.commit()
        
        query = 'UPDATE public.orders \
            SET order_id=(select order_id from order_lists order by order_id desc limit 1)+1 \
            WHERE user_id = %s and order_id isnull;'
        cursor.execute(query,(func.user_id(username),),)
        connection.commit()

        query2 = 'INSERT INTO public.order_lists(\
                    user_id)\
                    VALUES (%s);'
        cursor.execute(query2,(func.user_id(username),),)
        connection.commit()
        for row in orders:
                arr.append({
                    "user_id": str(row[0]),
                    "menu_id" : str(row[1]),
                    "menu_nama": str(row[2]),
                    "jumlah": str(row[3])
                })
        return jsonify(arr), 200
       

@app.route('/coffeekiran/search', methods=['GET'])
def search_menu():
    arr = []
    menu = rq.args.get('menu')
    # logger.debug(menu)

    connection = connect()
    cursor = connection.cursor()
    postgreSQL_select_Query = f"SELECT id, name, stock, price FROM menus WHERE stock > 0 and name ILIKE '%{menu}%'"

    cursor.execute(postgreSQL_select_Query)
    menus = cursor.fetchall()
    # logger.debug(menus)
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
            "jumlah_pesanan = ": str(row[2])
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
            "total_pesanan = ": str(row[2])
        })

    return jsonify(arr)


if __name__ == '__main__':
    app.run(debug=True)