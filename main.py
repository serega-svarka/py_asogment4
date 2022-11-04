from flask import Flask, request, session, redirect, url_for, render_template, flash
import requests
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

headers = {
 "X-RapidAPI-Key": "79e45bf277msh84f2840e7a48c1dp1fed2bjsnd23c661c5706",
}

app = Flask(__name__)
app.secret_key = "bkvdsfkbvsfudbhsdfbhuo"

conn = psycopg2.connect(database="PyProject_db", user="postgres", password="123", host="127.0.0.1", port="5432")


@app.route('/', methods=["POST", "GET"])
def index():
    if 'loggedin' in session:
        if request.method == 'POST':
            nft = request.form["nftname"]
            return redirect(url_for("nft", nft=nft))
        else:
            return render_template('index.html')

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cur.fetchone()

        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['username'] = account['username']
                return redirect(url_for('index'))
            else:
                flash('Incorrect username/password')
        else:
            flash('Incorrect username/password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        repass = request.form['repass']

        if password == repass:

            _hashed_password = generate_password_hash(password)

            cur.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cur.fetchone()

            if account:
                flash('Account already exists!')
            else:

                cur.execute("INSERT INTO users (fullname, username, password) VALUES (%s,%s,%s) RETURNING *", (fullname, username, _hashed_password))
                account = cur.fetchone()
                conn.commit()
                session['loggedin'] = True
                session['username'] = account['username']
                return redirect(url_for('index'))

        else:
            flash('Passwords do not match')
    elif request.method == 'POST':

      flash('Please fill out the form!')

    return render_template('register.html')


@app.route('/Error')
def error():
    return render_template('Error.html')


@app.route("/Game", methods=["POST", "GET"])
def nft():
    nftid = request.args.get('nft')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.args.get('specs') == "recommended":
        cur.execute("SELECT nftmeta FROM nfts", (nftid,))
        data = cur.fetchall()
    else:
        return render_template('Game.html', Game=data[0])
    if len(data):
        return render_template('Game.html', Game=data[0])
    else:
        url = "https://solana-gateway.moralis.io/nft/mainnet/{}/metadata"+(((nftid.replace(":", "")).replace("’", "")).replace("'", "")).replace(" ", "-")

        response = requests.request("GET", url, headers=headers)

        try:
            rNft=response.json()["nftmeta"]["Metadata:"]
        except:
            rNft="No nts info"

        else:

            cur.execute("INSERT INTO nfts (nft_name) VALUES (%s)",
                        (nftid))
            conn.commit()
            if request.args.get('nft') == "nftmeta":
                cur.execute("SELECT nft_meta FROM nfts WHERE nft_name = %s", (nft_id,))
                data = cur.fetchall()
                cur.close()
            else:
                cur.execute("SELECT nft_meta FROM minimalnfts WHERE nft_name = %s", (nftid,))
                data = cur.fetchall()
                cur.close()
            return render_template('Nft.html', Game=data[0])


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('username', None)

   return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
