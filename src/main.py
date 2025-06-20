import os
import sys
import logging
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.models import db
from src.routes.user import user_bp
from src.routes.products import product_bp
from src.routes.orders import order_bp
from src.routes.categories import category_bp
from src.routes.auth import auth_bp

# 設置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.logger.setLevel(logging.DEBUG)

# 啟用 CORS
CORS(app)

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 健康檢查端點
@app.route('/health')
def health_check():
    logger.debug("Health check requested")
    return {'status': 'healthy', 'service': 'ruten-api-service'}

with app.app_context():
    logger.info("Creating database tables")
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        logger.error("Static folder not configured")
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        logger.debug(f"Serving static file: {path}")
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            logger.debug("Serving index.html")
            return send_from_directory(static_folder_path, 'index.html')
        else:
            logger.error("index.html not found")
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=8000, debug=True)
