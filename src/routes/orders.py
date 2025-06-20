from flask import Blueprint, request, jsonify
from src.models.models import db, Order
from src.utils.ruten_client import RutenAPIClient
import json
from datetime import datetime

order_bp = Blueprint('orders', __name__)

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    """查詢訂單列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 30, type=int)
        status = request.args.get('status', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 從本地資料庫查詢
        query = Order.query
        
        if status != 'all':
            query = query.filter(Order.status == status)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y%m%d')
                query = query.filter(Order.order_date >= start_dt)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid start_date format. Use YYYYMMDD'
                }), 400
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y%m%d')
                query = query.filter(Order.order_date <= end_dt)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid end_date format. Use YYYYMMDD'
                }), 400
        
        orders = query.order_by(Order.order_date.desc()).paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'orders': [order.to_dict() for order in orders.items],
                'total': orders.total,
                'page': page,
                'page_size': page_size,
                'pages': orders.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """取得單一訂單資訊"""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({
            'status': 'success',
            'data': order.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders/<int:order_id>/ship', methods=['POST'])
def ship_order(order_id):
    """訂單出貨"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # 更新本地訂單狀態
        order.status = 'shipped'
        order.ship_date = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if order.ruten_order_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                shipping_data = {
                    'shipping_method': data.get('shipping_method', ''),
                    'tracking_number': data.get('tracking_number', ''),
                    'shipping_note': data.get('shipping_note', '')
                }
                result = client.ship_order(order.ruten_order_id, shipping_data)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'warning',
                        'message': 'Local order updated but failed to sync to Ruten',
                        'data': order.to_dict(),
                        'ruten_error': result.get('message')
                    })
                    
            except Exception as e:
                return jsonify({
                    'status': 'warning',
                    'message': 'Local order updated but failed to sync to Ruten',
                    'data': order.to_dict(),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'data': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消訂單"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        reason = data.get('reason', 'Customer request')
        
        # 更新本地訂單狀態
        order.status = 'cancelled'
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if order.ruten_order_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                result = client.cancel_order(order.ruten_order_id, reason)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'warning',
                        'message': 'Local order updated but failed to sync to Ruten',
                        'data': order.to_dict(),
                        'ruten_error': result.get('message')
                    })
                    
            except Exception as e:
                return jsonify({
                    'status': 'warning',
                    'message': 'Local order updated but failed to sync to Ruten',
                    'data': order.to_dict(),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'data': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders/<int:order_id>/refund', methods=['POST'])
def refund_order(order_id):
    """訂單退款"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # 更新本地訂單狀態
        order.status = 'refunded'
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if order.ruten_order_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                refund_data = {
                    'refund_amount': data.get('refund_amount', order.total_amount),
                    'refund_reason': data.get('refund_reason', 'Customer request'),
                    'refund_note': data.get('refund_note', '')
                }
                result = client.refund_order(order.ruten_order_id, refund_data)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'warning',
                        'message': 'Local order updated but failed to sync to Ruten',
                        'data': order.to_dict(),
                        'ruten_error': result.get('message')
                    })
                    
            except Exception as e:
                return jsonify({
                    'status': 'warning',
                    'message': 'Local order updated but failed to sync to Ruten',
                    'data': order.to_dict(),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'data': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders/sync', methods=['POST'])
def sync_orders_from_ruten():
    """從露天拍賣同步訂單資料"""
    try:
        client = RutenAPIClient()
        
        # 取得查詢參數
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        order_status = request.args.get('order_status', 'All')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 30, type=int)
        
        result = client.get_orders(
            start_date=start_date,
            end_date=end_date,
            order_status=order_status,
            page=page,
            page_size=page_size
        )
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to fetch orders from Ruten')
            }), 500
        
        synced_count = 0
        orders_data = result.get('data', {}).get('orders', [])
        
        for order_data in orders_data:
            ruten_order_id = order_data.get('order_id')
            
            # 檢查是否已存在
            existing_order = Order.query.filter_by(ruten_order_id=ruten_order_id).first()
            
            # 解析訂單日期
            order_date = None
            if order_data.get('order_date'):
                try:
                    order_date = datetime.strptime(order_data['order_date'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        order_date = datetime.strptime(order_data['order_date'], '%Y%m%d')
                    except ValueError:
                        pass
            
            if existing_order:
                # 更新現有訂單
                existing_order.buyer_name = order_data.get('buyer_name', existing_order.buyer_name)
                existing_order.total_amount = order_data.get('total_amount', existing_order.total_amount)
                existing_order.status = order_data.get('status', existing_order.status)
                if order_date:
                    existing_order.order_date = order_date
                existing_order.updated_at = datetime.utcnow()
            else:
                # 建立新訂單
                new_order = Order(
                    ruten_order_id=ruten_order_id,
                    buyer_name=order_data.get('buyer_name', ''),
                    total_amount=order_data.get('total_amount', 0),
                    status=order_data.get('status', 'pending'),
                    order_date=order_date
                )
                db.session.add(new_order)
            
            synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully synced {synced_count} orders',
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

@order_bp.route('/orders/detail', methods=['POST'])
def get_order_details():
    """查詢訂單明細"""
    try:
        data = request.get_json()
        order_ids = data.get('order_ids', [])
        
        if not order_ids:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: order_ids'
            }), 400
        
        client = RutenAPIClient()
        result = client.get_order_detail(order_ids)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to fetch order details from Ruten')
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

