import os
import logging
import hmac
import hashlib
import json
import time
import requests
import urllib.parse
from typing import Dict, Any

class RutenAPIClient:
    """露天拍賣 API 客戶端 - 僅限查詢商品相關功能"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, salt_key: str = None):
        self.base_url = "https://partner.ruten.com.tw"
        self.api_key = api_key or os.getenv('RUTEN_API_KEY')
        self.secret_key = secret_key or os.getenv('RUTEN_SECRET_KEY')
        self.salt_key = salt_key or os.getenv('RUTEN_SALT_KEY')
        
        if not all([self.api_key, self.secret_key, self.salt_key]):
            raise ValueError("Missing required credentials: RUTEN_API_KEY, RUTEN_SECRET_KEY, RUTEN_SALT_KEY")
        
        # 設置日誌
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logging.debug(f"Initialized with api_key={self.api_key[:8]}..., secret_key={self.secret_key[:8]}..., salt_key={self.salt_key}")
    
    def _generate_signature(self, url_path: str, request_body: str = "", timestamp: str = None, params: Dict[str, Any] = None) -> tuple:
        """生成 HMAC-SHA256 簽章"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        # 處理查詢參數
        if params:
            query_string = urllib.parse.urlencode(params, doseq=True)
            url_path = f"{url_path}?{query_string}" if query_string else url_path
        
        # 組合簽章字串: Salt Key + URL Path + Request Body + Timestamp
        sign_string = f"{self.salt_key}{url_path}{request_body}{timestamp}"
        logging.debug(f"Signature string: {sign_string}, timestamp: {timestamp}")
        
        # 計算 HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def _get_headers(self, url_path: str, request_body: str = "", content_type: str = "application/json", params: Dict[str, Any] = None) -> Dict[str, str]:
        """生成請求標頭"""
        signature, timestamp = self._generate_signature(url_path, request_body, params=params)
        logging.debug(f"Generated headers with signature={signature[:8]}..., timestamp={timestamp}")
        
        return {
            'Host': 'partner.ruten.com.tw',
            'Content-Type': content_type,
            'X-RT-Key': self.api_key,
            'X-RT-Timestamp': timestamp,
            'X-RT-Authorization': signature
        }
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """發送 API 請求"""
        url = f"{self.base_url}{endpoint}"
        request_body = ""
        
        headers = self._get_headers(endpoint, request_body, params=params)
        logging.debug(f"Ruten API request: {method} {url}, headers={headers}, params={params}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            logging.debug(f"Ruten API response: status={response.status_code}, body={result}")
            if result.get('status') == 'success':
                logging.info(f"API call successful: endpoint={endpoint}, status={result.get('status')}")
            else:
                logging.error(f"API call failed: endpoint={endpoint}, status={result.get('status')}, error_code={result.get('error_code')}, error_msg={result.get('error_msg')}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_response = {
                'error': True,
                'message': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'response_body': getattr(e.response, 'text', 'No response body') if hasattr(e, 'response') else 'No response'
            }
            try:
                if hasattr(e, 'response') and e.response:
                    error_body = e.response.json()
                    error_response['error_code'] = error_body.get('error_code')
                    error_response['error_msg'] = error_body.get('error_msg')
                    logging.error(f"Ruten API error: endpoint={endpoint}, status_code={error_response['status_code']}, error_code={error_response['error_code']}, error_msg={error_response['error_msg']}, response_body={error_response['response_body']}")
                else:
                    logging.error(f"Ruten API error: endpoint={endpoint}, message={error_response['message']}, no response body available")
            except (ValueError, AttributeError):
                logging.error(f"Ruten API error: endpoint={endpoint}, status_code={error_response['status_code']}, message={error_response['message']}, response_body={error_response['response_body']}")
            return error_response
    
    def get_products(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """查詢商品列表"""
        params = {'page': page, 'page_size': page_size}
        result = self._make_request('GET', '/api/v1/product/list', params=params)
        if result.get('status') == 'success' and not result.get('data'):
            logging.info(f"No products found for page {page} with page_size {page_size}")
        return result
    
    def get_product(self, item_id: str) -> Dict[str, Any]:
        """取得商品資訊"""
        result = self._make_request('GET', f'/api/v1/product/item/{item_id}')
        if result.get('status') == 'success' and not result.get('data'):
            logging.info(f"No product found for item_id {item_id}")
        return result
    
    def verify_credentials(self) -> Dict[str, Any]:
        """驗證 API 憑證"""
        try:
            result = self.get_products()
            logging.debug(f"Verify credentials response: {result}")
            if 'error' in result:
                logging.error(f"Credential verification failed: message={result.get('message', 'Unknown error')}")
                return {'valid': False, 'message': result.get('message', 'Unknown error')}
            return {'valid': True, 'message': 'Credentials are valid'}
        except Exception as e:
            logging.error(f"Verify credentials error: {str(e)}")
            return {'valid': False, 'message': str(e)}
