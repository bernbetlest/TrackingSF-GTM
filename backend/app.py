from flask import Flask, jsonify, request, Response
from flask_mysqldb import MySQL
from db_config import db_config
from flask_cors import CORS
from datetime import datetime, timedelta
import csv
import io

app = Flask(__name__)

CORS(app)
# Konfigurasi database
app.config.update(db_config)

mysql = MySQL(app)

@app.route('/')
def home():
    return 'API Flask terhubung ke XAMPP!'

@app.route('/track', methods=['GET'])
def get_user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM track")  
    results = cur.fetchall()
    track = [{'no': row[0], 'waktu_login': row[1], 'sf_id': row[2], 'notelp':row[3], 'branch':row[4], 'wok':row[5]} for row in results]
    return jsonify(track)

@app.route('/api/login_user/', methods=['POST'])
def user_verification():
    data = request.get_json()
    sf_id = data.get('sf_id')
    notelp = data.get('notelp')

    if not sf_id or not notelp:
        return jsonify({'status': 'fail', 'message': 'Missing data'}), 400

    cur = mysql.connection.cursor()
    query = "SELECT * FROM user WHERE sf_id = %s AND notelp = %s"
    cur.execute(query, (sf_id, notelp))
    user = cur.fetchone()

    if user:
        branch = user[2]
        wok = user[3]
        # Insert login info to 'track' table
        waktu_login =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = """
            INSERT INTO track (waktu_login, sf_id, notelp, branch, wok)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (waktu_login, sf_id, notelp, branch, wok))
        mysql.connection.commit()

        cur.close()
        return jsonify({'status': 'success'})
    else:
        cur.close()
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'})
    

@app.route('/api/login_admin/', methods=['POST'])
def admin_verification():
    dataadmin = request.get_json()
    Username = dataadmin.get('Username')
    Password = dataadmin.get('Password')

    if not Username or not Password:
        return jsonify({'status': 'fail', 'message': 'Missing data'}), 400

    cur = mysql.connection.cursor()
    query = "SELECT * FROM admin WHERE Username = %s AND Password = %s"
    cur.execute(query, (Username, Password))
    admin = cur.fetchone()
    

    if admin:
        cur.close()
        return jsonify({'status': 'success'})
    else:
        cur.close()
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'}),


@app.route("/track/download")
def download_csv():
    cur = mysql.connection
    cursor = cur.cursor()
    cursor.execute("SELECT * FROM track")  
    rows = cursor.fetchall()

    # Ambil nama kolom dari cursor
    column_names = [i[0] for i in cursor.description]

    # Buat CSV di memory
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(column_names)  # header
    cw.writerows(rows)         # isi data

    output = si.getvalue()
    si.close()

    cursor.close()

    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=track_data.csv"}
    )    

if __name__ == '__main__':
    app.run(debug=True)



    