from flask import Blueprint, request, jsonify
from src.models.models import db, Product
from src.utils.ruten_client import RutenAPIClient
import json
from datetime import datetime

product_bp = Blueprint('products', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """查詢商品列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 30, type=int)
        status = request.args.get('status', 'all')
        
        # 從本地資料庫查詢
        query = Product.query
        if status != 'all':
            query = query.filter(Product.status == status)
        
        products = query.paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'products': [product.to_dict() for product in products.items],
                'total': products.total,
                'page': page,
                'page_size': page_size,
                'pages': products.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """取得單一商品資訊"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products', methods=['POST'])
def create_product():
    """新增商品"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['title', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # 建立新商品
        product = Product(
            title=data['title'],
            description=data.get('description', ''),
            price=data['price'],
            stock=data.get('stock', 0),
            status=data.get('status', 'offline'),
            category_id=data.get('category_id')
        )
        
        db.session.add(product)
        db.session.commit()
        
        # 如果需要同步到露天拍賣
        if data.get('sync_to_ruten', False):
            try:
                client = RutenAPIClient()
                ruten_data = {
                    'title': data['title'],
                    'description': data.get('description', ''),
                    'price': data['price'],
                    'stock': data.get('stock', 0)
                }
                result = client.create_product(ruten_data)
                
                if 'error' not in result:
                    # 更新本地商品的露天商品ID
                    product.ruten_item_id = result.get('item_id')
                    db.session.commit()
                    
            except Exception as e:
                # 記錄錯誤但不影響本地建立
                print(f"Failed to sync to Ruten: {e}")
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新商品資訊"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # 更新欄位
        if 'title' in data:
            product.title = data['title']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'stock' in data:
            product.stock = data['stock']
        if 'status' in data:
            product.status = data['status']
        if 'category_id' in data:
            product.category_id = data['category_id']
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>/stock', methods=['PUT'])
def update_product_stock(product_id):
    """更新商品庫存"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'stock' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: stock'
            }), 400
        
        product.stock = data['stock']
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if product.ruten_item_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                client.update_product_stock(product.ruten_item_id, data['stock'])
            except Exception as e:
                print(f"Failed to sync stock to Ruten: {e}")
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>/price', methods=['PUT'])
def update_product_price(product_id):
    """更新商品價格"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'price' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: price'
            }), 400
        
        product.price = data['price']
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if product.ruten_item_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                client.update_product_price(product.ruten_item_id, data['price'])
            except Exception as e:
                print(f"Failed to sync price to Ruten: {e}")
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>/status', methods=['PUT'])
def update_product_status(product_id):
    """更新商品狀態 (上架/下架)"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: status'
            }), 400
        
        if data['status'] not in ['online', 'offline']:
            return jsonify({
                'status': 'error',
                'message': 'Status must be either "online" or "offline"'
            }), 400
        
        product.status = data['status']
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if product.ruten_item_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                if data['status'] == 'online':
                    client.set_product_online(product.ruten_item_id)
                else:
                    client.set_product_offline(product.ruten_item_id)
            except Exception as e:
                print(f"Failed to sync status to Ruten: {e}")
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """刪除商品"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # 先下架露天拍賣商品
        if product.ruten_item_id:
            try:
                client = RutenAPIClient()
                client.set_product_offline(product.ruten_item_id)
            except Exception as e:
                print(f"Failed to offline product on Ruten: {e}")
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@product_bp.route('/products/sync', methods=['POST'])
def sync_products_from_ruten():
    """從露天拍賣同步商品資料"""
    try:
        client = RutenAPIClient()
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 30, type=int)
        
        result = client.get_products(page=page, page_size=page_size)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to fetch products from Ruten')
            }), 500
        
        synced_count = 0
        products_data = result.get('data', {}).get('products', [])
        
        for product_data in products_data:
            ruten_item_id = product_data.get('item_id')
            
            # 檢查是否已存在
            existing_product = Product.query.filter_by(ruten_item_id=ruten_item_id).first()
            
            if existing_product:
                # 更新現有商品
                existing_product.title = product_data.get('title', existing_product.title)
                existing_product.price = product_data.get('price', existing_product.price)
                existing_product.stock = product_data.get('stock', existing_product.stock)
                existing_product.status = product_data.get('status', existing_product.status)
                existing_product.updated_at = datetime.utcnow()
            else:
                # 建立新商品
                new_product = Product(
                    ruten_item_id=ruten_item_id,
                    title=product_data.get('title', ''),
                    description=product_data.get('description', ''),
                    price=product_data.get('price', 0),
                    stock=product_data.get('stock', 0),
                    status=product_data.get('status', 'offline')
                )
                db.session.add(new_product)
            
            synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully synced {synced_count} products',
            'data': {
                'synced_count': synced_count,
                'page': page,
                'page_size': page_size
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

