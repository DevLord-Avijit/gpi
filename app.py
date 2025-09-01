from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import uuid, qrcode, io, json, decimal, re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# ----------------- Data Stores -----------------
USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transactions.json"
notifications = {}  # gpi_id -> list of notifications

# ----------------- Helpers -----------------
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_transactions():
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_transactions(tx_list):
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(tx_list, f, indent=2)

def authenticate(token):
    users = load_users()
    for gpi_id, user in users.items():
        if user.get("token") == token:
            return gpi_id
    return None

def add_notification(gpi_id, message):
    if gpi_id not in notifications:
        notifications[gpi_id] = []
    notifications[gpi_id].append({"message": message, "timestamp": datetime.now().isoformat()})

def ensure_default_user():
    users = load_users()
    if not users:
        users["test@gpi"] = {
            "name": "Test User",
            "balance": 1000.0,
            "password": "1234",
            "token": ""
        }
        save_users(users)

# ----------------- Web Routes -----------------
@app.route("/")
def home():
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    ensure_default_user()
    if request.method == "POST":
        gpi_id = request.form.get("gpi_id")
        password = request.form.get("password")
        users = load_users()
        if gpi_id in users and users[gpi_id]["password"] == password:
            token = str(uuid.uuid4())
            users[gpi_id]["token"] = token
            save_users(users)
            add_notification(gpi_id, "Logged in successfully.")
            return redirect(url_for("dashboard", token=token))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard/<token>", methods=["GET", "POST"])
def dashboard(token):
    gpi_id = authenticate(token)
    if not gpi_id:
        return redirect(url_for("login_page"))

    users = load_users()
    user = users[gpi_id]
    transactions = load_transactions()
    user_tx = [tx for tx in transactions if tx["from"] == gpi_id or tx["to"] == gpi_id]

    if request.method == "POST":
        gpi_id_to = request.form.get("to")
        try:
            amount = float(decimal.Decimal(request.form.get("amount")).quantize(decimal.Decimal("0.01")))
        except:
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Invalid amount", gpi_id=gpi_id)

        # Validations
        if amount < 1:
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Minimum amount is 1 GPI", gpi_id=gpi_id)
        if amount != round(amount, 2):
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Amount can have at most 2 decimal places", gpi_id=gpi_id)
        if gpi_id_to not in users:
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Recipient not found", gpi_id=gpi_id)
        if gpi_id_to == gpi_id:
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Cannot send money to yourself", gpi_id=gpi_id)
        if user["balance"] < amount:
            return render_template("dashboard.html", user=user, transactions=user_tx, token=token,
                                   error="Insufficient balance", gpi_id=gpi_id)

        # Process transaction
        user["balance"] -= amount
        users[gpi_id_to]["balance"] += amount
        save_users(users)

        tx_id = str(uuid.uuid4())
        tx = {
            "tx_id": tx_id,
            "from": gpi_id,
            "to": gpi_id_to,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        transactions.append(tx)
        save_transactions(transactions)

        socketio.emit('transaction_update', {'tx': tx}, room=gpi_id)
        socketio.emit('transaction_update', {'tx': tx}, room=gpi_id_to)

        add_notification(gpi_id, f"Paid {amount} GPI to {gpi_id_to}.")
        add_notification(gpi_id_to, f"Received {amount} GPI from {gpi_id}.")

        return redirect(url_for("dashboard", token=token))

    return render_template("dashboard.html", user=user, transactions=user_tx, token=token, gpi_id=gpi_id)

# ----------------- Mobile Payment Page -----------------
@app.route("/mobile_dashboard/<token>", methods=["GET", "POST"])
def mobile_dashboard(token):
    gpi_id = authenticate(token)
    if not gpi_id:
        return redirect(url_for("login_page"))
    users = load_users()
    user = users[gpi_id]

    if request.method == "POST":
        gpi_id_to = request.form.get("to")
        try:
            amount = float(decimal.Decimal(request.form.get("amount")).quantize(decimal.Decimal("0.01")))
        except:
            return render_template("mobile_dashboard.html", user=user, error="Invalid amount", gpi_id=gpi_id)

        # Same validations as desktop
        if amount < 1 or amount != round(amount, 2) or gpi_id_to not in users or gpi_id_to == gpi_id or user["balance"] < amount:
            return render_template("mobile_dashboard.html", user=user, error="Invalid transaction", gpi_id=gpi_id)

        # Process transaction
        user["balance"] -= amount
        users[gpi_id_to]["balance"] += amount
        save_users(users)

        tx_id = str(uuid.uuid4())
        tx = {
            "tx_id": tx_id,
            "from": gpi_id,
            "to": gpi_id_to,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        transactions = load_transactions()
        transactions.append(tx)
        save_transactions(transactions)

        socketio.emit('transaction_update', {'tx': tx}, room=gpi_id)
        socketio.emit('transaction_update', {'tx': tx}, room=gpi_id_to)

        add_notification(gpi_id, f"Paid {amount} GPI to {gpi_id_to}.")
        add_notification(gpi_id_to, f"Received {amount} GPI from {gpi_id}.")

        return render_template("mobile_dashboard.html", user=user, success="Payment successful!", gpi_id=gpi_id)

    return render_template("mobile_dashboard.html", user=user, gpi_id=gpi_id)

# ----------------- QR Code -----------------
@app.route("/qr/<gpi_id>")
def generate_qr(gpi_id):
    users = load_users()
    if gpi_id not in users:
        return f"User '{gpi_id}' not found", 404

    amount = request.args.get("amount", 0)
    qr_data = f"gpi://pay?to={gpi_id}&amount={amount}"

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# ----------------- SocketIO -----------------
@socketio.on('join')
def on_join(data):
    gpi_id = data.get('gpi_id')
    join_room(gpi_id)

# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

