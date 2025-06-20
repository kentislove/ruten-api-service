from flask import Blueprint, request, jsonify
from src.models.models import db, Category
from src.utils.ruten_client import RutenAPIClient
import json
from datetime import datetime

category_bp = Blueprint('categories', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    """查詢分類列表"""
    try:
        # 從本地資料庫查詢
        categories = Category.query.all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'categories': [category.to_dict() for category in categories]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@category_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """取得單一分類資訊"""
    try:
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'status': 'success',
            'data': category.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@category_bp.route('/categories', methods=['POST'])
def create_category():
    """新增分類"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        if 'name' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: name'
            }), 400
        
        # 建立新分類
        category = Category(
            name=data['name'],
            parent_id=data.get('parent_id')
        )
        
        db.session.add(category)
        db.session.commit()
        
        # 如果需要同步到露天拍賣
        if data.get('sync_to_ruten', False):
            try:
                client = RutenAPIClient()
                ruten_data = {
                    'name': data['name'],
                    'parent_id': data.get('parent_id')
                }
                result = client.create_category(ruten_data)
                
                if 'error' not in result:
                    # 更新本地分類的露天分類ID
                    category.ruten_category_id = result.get('category_id')
                    db.session.commit()
                    
            except Exception as e:
                # 記錄錯誤但不影響本地建立
                print(f"Failed to sync to Ruten: {e}")
        
        return jsonify({
            'status': 'success',
            'data': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分類資訊"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        # 更新欄位
        if 'name' in data:
            category.name = data['name']
        if 'parent_id' in data:
            category.parent_id = data['parent_id']
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 同步到露天拍賣
        if category.ruten_category_id and data.get('sync_to_ruten', True):
            try:
                client = RutenAPIClient()
                ruten_data = {
                    'category_id': category.ruten_category_id,
                    'name': category.name,
                    'parent_id': category.parent_id
                }
                result = client.update_category(ruten_data)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'warning',
                        'message': 'Local category updated but failed to sync to Ruten',
                        'data': category.to_dict(),
                        'ruten_error': result.get('message')
                    })
                    
            except Exception as e:
                return jsonify({
                    'status': 'warning',
                    'message': 'Local category updated but failed to sync to Ruten',
                    'data': category.to_dict(),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'data': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """刪除分類"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # 檢查是否有子分類
        child_categories = Category.query.filter_by(parent_id=category_id).count()
        if child_categories > 0:
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete category with child categories'
            }), 400
        
        # 同步刪除露天拍賣分類
        if category.ruten_category_id:
            try:
                client = RutenAPIClient()
                result = client.delete_category(category.ruten_category_id)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'error',
                        'message': f'Failed to delete category on Ruten: {result.get("message")}'
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to delete category on Ruten: {str(e)}'
                }), 500
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Category deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@category_bp.route('/categories/sync', methods=['POST'])
def sync_categories_from_ruten():
    """從露天拍賣同步分類資料"""
    try:
        client = RutenAPIClient()
        result = client.get_categories()
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to fetch categories from Ruten')
            }), 500
        
        synced_count = 0
        categories_data = result.get('data', {}).get('categories', [])
        
        for category_data in categories_data:
            ruten_category_id = category_data.get('category_id')
            
            # 檢查是否已存在
            existing_category = Category.query.filter_by(ruten_category_id=ruten_category_id).first()
            
            if existing_category:
                # 更新現有分類
                existing_category.name = category_data.get('name', existing_category.name)
                existing_category.parent_id = category_data.get('parent_id', existing_category.parent_id)
                existing_category.updated_at = datetime.utcnow()
            else:
                # 建立新分類
                new_category = Category(
                    ruten_category_id=ruten_category_id,
                    name=category_data.get('name', ''),
                    parent_id=category_data.get('parent_id')
                )
                db.session.add(new_category)
            
            synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully synced {synced_count} categories',
            'data': {
                'synced_count': synced_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

