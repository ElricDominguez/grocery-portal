from flask import Flask, render_template, request, redirect, session
import db_config

app = Flask(__name__)
app.secret_key = "supersecretkey"  # 🔐 Needed for session support. Change this before deployment.

#add_to_cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = str(request.form["product_id"])

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    # Add or increment quantity
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart
    return redirect("/products")


#cart
@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    if not cart:
        return "🛒 Your cart is empty."

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(cart))
    query = f"SELECT * FROM products WHERE id IN ({placeholders})"
    cursor.execute(query, list(cart.keys()))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    # Add quantity info
    for p in products:
        pid = str(p["id"])
        p["quantity"] = cart[pid]
        p["subtotal"] = round(p["price"] * p["quantity"], 2)

    total = round(sum(p["subtotal"] for p in products), 2)

    return render_template("cart.html", products=products, total=total)
#checkout
from datetime import datetime

@app.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    cart = session.get("cart", {})
    if not cart:
        return "❌ Cart is empty."

    conn = db_config.get_connection()
    cursor = conn.cursor()

    # Get product prices to calculate total
    placeholders = ",".join(["%s"] * len(cart))
    cursor.execute(f"SELECT id, price FROM products WHERE id IN ({placeholders})", list(cart.keys()))
    prices = {str(row[0]): float(row[1]) for row in cursor.fetchall()}

    total = sum(prices[pid] * qty for pid, qty in cart.items())

    # Insert order
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (%s, %s)", (session["user_id"], total))
    order_id = cursor.lastrowid

    # Insert order items
    for pid, qty in cart.items():
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, pid, qty, prices[pid])
        )

    conn.commit()
    cursor.close()
    conn.close()

    session.pop("cart", None)
    return f"Order #{order_id} placed successfully!"
#orders 
#used to view past orders
@app.route("/orders")
def view_orders():
    if "user_id" not in session:
        return redirect("/login")

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (session["user_id"],))
    orders = cursor.fetchall()

    for o in orders:
        cursor.execute("""
            SELECT p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = %s
        """, (o["id"],))
        o["items"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("orders.html", orders=orders)

#products
@app.route("/products")
def products():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("products.html", products=items)

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = db_config.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return f"Welcome, {user['name']}!"
        else:
            return "Invalid email or password."

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
