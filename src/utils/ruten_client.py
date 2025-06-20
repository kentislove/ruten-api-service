import os
import hashlib
import hmac
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional

class RutenAPIClient:
    """露天拍賣 API 客戶端"""
    
    def __init__(self):
        self.base_url = "https://partner.ruten.com.tw"
        self.api_key = os.getenv('RUTEN_API_KEY')
        self.secret_key = os.getenv('RUTEN_SECRET_KEY')
        self.salt_key = os.getenv('RUTEN_SALT_KEY')
        
        if not all([self.api_key, self.secret_key, self.salt_key]):
            raise ValueError("Missing required environment variables: RUTEN_API_KEY, RUTEN_SECRET_KEY, RUTEN_SALT_KEY")
    
    def _generate_signature(self, url_path: str, request_body: str = "", timestamp: str = None) -> tuple:
        """生成 HMAC-SHA256 簽章"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        # 組合簽章字串: Salt Key + URL Path + Request Body + Timestamp
        sign_string = f"{self.salt_key}{url_path}{request_body}{timestamp}"
        
        # 計算 HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def _get_headers(self, url_path: str, request_body: str = "", content_type: str = "application/json") -> Dict[str, str]:
        """生成請求標頭"""
        signature, timestamp = self._generate_signature(url_path, request_body)
        
        return {
            'Host': 'partner.ruten.com.tw',
            'Content-Type': content_type,
            'X-RT-Key': self.api_key,
            'X-RT-Timestamp': timestamp,
            'X-RT-Authorization': signature
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """發送 API 請求"""
        url = f"{self.base_url}{endpoint}"
        request_body = ""
        
        if data:
            import json
            request_body = json.dumps(data, ensure_ascii=False)
        
        headers = self._get_headers(endpoint, request_body)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=request_body, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=request_body, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    # 商品相關 API
    def get_products(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """查詢商品列表"""
        params = {
            'page': page,
            'page_size': page_size
        }
        return self._make_request('GET', '/api/v1/product/list', params=params)
    
    def get_product(self, item_id: str) -> Dict[str, Any]:
        """取得商品資訊"""
        return self._make_request('GET', f'/api/v1/product/item/{item_id}')
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """新增商品"""
        return self._make_request('POST', '/api/v1/product/item', data=product_data)
    
    def update_product_stock(self, item_id: str, stock: int) -> Dict[str, Any]:
        """更新商品庫存"""
        data = {'item_id': item_id, 'stock': stock}
        return self._make_request('PUT', '/api/v1/product/item/stock', data=data)
    
    def update_product_price(self, item_id: str, price: float) -> Dict[str, Any]:
        """更新商品價格"""
        data = {'item_id': item_id, 'price': price}
        return self._make_request('PUT', '/api/v1/product/item/price', data=data)
    
    def set_product_online(self, item_id: str) -> Dict[str, Any]:
        """上架商品"""
        data = {'item_id': item_id}
        return self._make_request('PUT', '/api/v1/product/item/online', data=data)
    
    def set_product_offline(self, item_id: str) -> Dict[str, Any]:
        """下架商品"""
        data = {'item_id': item_id}
        return self._make_request('PUT', '/api/v1/product/item/offline', data=data)
    
    # 訂單相關 API
    def get_orders(self, start_date: str = None, end_date: str = None, 
                   order_status: str = 'All', page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """查詢訂單列表"""
        params = {
            'order_status': order_status,
            'page': page,
            'page_size': page_size
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('GET', '/api/v1/order/list', params=params)
    
    def get_order_detail(self, order_ids: list) -> Dict[str, Any]:
        """查詢訂單明細"""
        data = {'order_ids': order_ids}
        return self._make_request('POST', '/api/v1/order/detail', data=data)
    
    def ship_order(self, order_id: str, shipping_data: Dict[str, Any]) -> Dict[str, Any]:
        """訂單出貨"""
        data = {'order_id': order_id, **shipping_data}
        return self._make_request('POST', '/api/v1/order/ship', data=data)
    
    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        """取消訂單"""
        data = {'order_id': order_id, 'reason': reason}
        return self._make_request('POST', '/api/v1/order/canceluse', data=data)
    
    def refund_order(self, order_id: str, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """訂單退款"""
        data = {'order_id': order_id, **refund_data}
        return self._make_request('POST', '/api/v1/order/refund', data=data)
    
    # 分類相關 API
    def get_categories(self) -> Dict[str, Any]:
        """查詢店舖分類列表"""
        return self._make_request('GET', '/api/v1/product/store_class/list')
    
    def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """新增店舖分類"""
        return self._make_request('POST', '/api/v1/product/store_class', data=category_data)
    
    def update_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新店舖分類"""
        return self._make_request('PUT', '/api/v1/product/store_class', data=category_data)
    
    def delete_category(self, category_id: str) -> Dict[str, Any]:
        """刪除店舖分類"""
        data = {'category_id': category_id}
        return self._make_request('DELETE', '/api/v1/product/store_class', data=data)
    
    def verify_credentials(self) -> Dict[str, Any]:
        """驗證 API 憑證"""
        try:
            # 嘗試呼叫一個簡單的 API 來驗證憑證
            result = self.get_categories()
            if 'error' in result:
                return {'valid': False, 'message': result.get('message', 'Unknown error')}
            return {'valid': True, 'message': 'Credentials are valid'}
        except Exception as e:
            return {'valid': False, 'message': str(e)}

