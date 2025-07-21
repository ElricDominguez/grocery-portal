from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Hello from your Grocery Portal!"

if __name__ == "__main__":
    app.run(debug=True)
