from flask import Flask, render_template
from flask_cors import CORS
from routes.api_routes import api_bp

app = Flask(__name__)
CORS(app)  # Allow Frontend to communicate with Backend

# Register Blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)