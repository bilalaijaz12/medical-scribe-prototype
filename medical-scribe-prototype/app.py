from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
from backend.routes.api import api_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            static_folder='frontend/static', 
            template_folder='frontend/templates')

# Enable CORS
CORS(app)

# Configuration
app.config.from_object('config')

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

# Main route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)