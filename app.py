from flask import Flask, render_template, request, redirect, session
import db_config
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "defaultkey") #final change, if broken replace line with: app.secret_key = "supersecretkey" 

# home route
@app.route("/")
def home():
    return redirect("/products")

# account
@app.route("/account", methods=["GET", "POST"])
def account():
    if "user_id" not in session:
        return redirect("/login")

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name, email FROM users WHERE id = %s", (session["user_id"],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("account.html", user=user)

# delete_account
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect("/login")

    conn = db_config.get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE user_id = %s)", (session["user_id"],))
    cursor.execute("DELETE FROM orders WHERE user_id = %s", (session["user_id"],))
    cursor.execute("DELETE FROM users WHERE id = %s", (session["user_id"],))

    conn.commit()
    cursor.close()
    conn.close()

    session.clear()
    return "Account deleted successfully. Refresh to return to home."

# add_to_cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = str(request.form["product_id"])

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart
    return redirect("/products")

# cart
@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    if not cart:
        return redirect("/products")

    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(cart))
    query = f"SELECT * FROM products WHERE id IN ({placeholders})"
    cursor.execute(query, list(cart.keys()))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    for p in products:
        pid = str(p["id"])
        p["quantity"] = cart[pid]
        p["price"] = float(p["price"])  # Fix Decimal -> float
        p["subtotal"] = round(p["price"] * p["quantity"], 2)

    subtotal = sum(p["subtotal"] for p in products)
    tax_rate = 0.0825
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    return render_template("cart.html", products=products, subtotal=subtotal, tax=tax, total=total)

# checkout
@app.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    cart = session.get("cart", {})
    if not cart:
        return "Cart is empty."

    conn = db_config.get_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(cart))
    cursor.execute(f"SELECT id, price FROM products WHERE id IN ({placeholders})", list(cart.keys()))
    prices = {str(row[0]): float(row[1]) for row in cursor.fetchall()}

    subtotal = sum(prices[pid] * qty for pid, qty in cart.items())
    tax_rate = 0.0825
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    # Insert the order
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (%s, %s)", (session["user_id"], total))
    order_id = cursor.lastrowid

     
    for pid, qty in cart.items():
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, pid, qty, prices[pid])
        )
        cursor.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s",
            (qty, pid)
        )

    conn.commit()
    cursor.close()
    conn.close()

    session.pop("cart", None)
    return redirect("/payment")


# payment
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        return redirect("/orders")
    return render_template("payment.html")

# orders
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

# products
@app.route("/products")
def products():
    conn = db_config.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("products.html", products=items)

# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = db_config.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            return redirect("/login")
        except Exception as e:
            return f"❌ Registration failed: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# login
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
            return redirect("/products")
        else:
            return "Invalid email or password."

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=False) #changed to false, originally true