from flask import Blueprint, request, jsonify
from src.utils.ruten_client import RutenAPIClient
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/verify', methods=['POST'])
def verify_credentials():
    """驗證 API 金鑰是否有效"""
    try:
        data = request.get_json()
        
        # 暫時設定環境變數進行驗證
        original_api_key = os.getenv('RUTEN_API_KEY')
        original_secret_key = os.getenv('RUTEN_SECRET_KEY')
        original_salt_key = os.getenv('RUTEN_SALT_KEY')
        
        try:
            # 設定新的憑證
            os.environ['RUTEN_API_KEY'] = data.get('api_key', '')
            os.environ['RUTEN_SECRET_KEY'] = data.get('secret_key', '')
            os.environ['RUTEN_SALT_KEY'] = data.get('salt_key', '')
            
            # 建立客戶端並驗證
            client = RutenAPIClient()
            result = client.verify_credentials()
            
            return jsonify({
                'status': 'success',
                'data': result
            })
            
        finally:
            # 恢復原始環境變數
            if original_api_key:
                os.environ['RUTEN_API_KEY'] = original_api_key
            if original_secret_key:
                os.environ['RUTEN_SECRET_KEY'] = original_secret_key
            if original_salt_key:
                os.environ['RUTEN_SALT_KEY'] = original_salt_key
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/status', methods=['GET'])
def get_auth_status():
    """取得目前認證狀態"""
    try:
        api_key = os.getenv('RUTEN_API_KEY')
        secret_key = os.getenv('RUTEN_SECRET_KEY')
        salt_key = os.getenv('RUTEN_SALT_KEY')
        
        has_credentials = bool(api_key and secret_key and salt_key)
        
        if has_credentials:
            try:
                client = RutenAPIClient()
                result = client.verify_credentials()
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'has_credentials': True,
                        'credentials_valid': result.get('valid', False),
                        'message': result.get('message', ''),
                        'api_key_preview': f"{api_key[:8]}..." if api_key else None
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'success',
                    'data': {
                        'has_credentials': True,
                        'credentials_valid': False,
                        'message': str(e),
                        'api_key_preview': f"{api_key[:8]}..." if api_key else None
                    }
                })
        else:
            return jsonify({
                'status': 'success',
                'data': {
                    'has_credentials': False,
                    'credentials_valid': False,
                    'message': 'No credentials configured'
                }
            })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

