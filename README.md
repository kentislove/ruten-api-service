# 露天拍賣 API 管理系統

## 專案概述

本專案是一個完整的露天拍賣 API 管理系統，提供商品、訂單與分類的統一管理平台。系統採用 Flask 後端 + 前端網頁的架構，可部署在 Render Free Plan 上，透過環境變數管理 API 金鑰，確保安全性與可維護性。

## 功能特色

### 🛍️ 商品管理
- 新增、編輯、刪除商品
- 更新商品價格與庫存
- 商品上架/下架管理
- 與露天拍賣 API 雙向同步

### 📦 訂單管理
- 查詢訂單列表與明細
- 訂單出貨處理
- 訂單取消與退款
- 訂單狀態追蹤

### 🏷️ 分類管理
- 建立商品分類階層
- 分類新增、編輯、刪除
- 與露天拍賣分類同步

### 🔐 安全認證
- HMAC-SHA256 簽章驗證
- 環境變數管理 API 金鑰
- 安全的 API 請求處理

### 🎨 現代化介面
- 響應式設計，支援桌面與行動裝置
- 直觀的操作介面
- 即時狀態更新與錯誤提示

## 技術架構

### 後端技術
- **Flask**: Python Web 框架
- **SQLAlchemy**: ORM 資料庫操作
- **SQLite**: 輕量級資料庫
- **Flask-CORS**: 跨域請求支援
- **Requests**: HTTP 請求處理

### 前端技術
- **HTML5**: 語義化標記
- **CSS3**: 現代化樣式與動畫
- **JavaScript ES6+**: 互動功能實作
- **Font Awesome**: 圖示庫

### 部署平台
- **Render**: 雲端部署平台
- **Gunicorn**: WSGI 伺服器
- **環境變數**: 安全配置管理

## 系統需求

- Python 3.11+
- 露天拍賣 API 憑證 (API Key, Secret Key, Salt Key)
- 網路連線

## 本地開發環境設定

### 1. 複製專案
```bash
git clone <repository-url>
cd ruten-api-service
```

### 2. 建立虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 4. 設定環境變數
建立 `.env` 檔案：
```bash
RUTEN_API_KEY=your_api_key_here
RUTEN_SECRET_KEY=your_secret_key_here
RUTEN_SALT_KEY=your_salt_key_here
SECRET_KEY=your_flask_secret_key
```

### 5. 啟動應用程式
```bash
python src/main.py
```

應用程式將在 `http://localhost:8000` 啟動。

## Render 部署指南

### 1. 準備 GitHub 儲存庫
將專案程式碼推送到 GitHub 儲存庫。

### 2. 建立 Render 服務
1. 登入 [Render](https://render.com)
2. 點擊 "New +" → "Web Service"
3. 連接 GitHub 儲存庫
4. 選擇專案儲存庫

### 3. 配置部署設定
- **Name**: `ruten-api-service`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`

### 4. 設定環境變數
在 Render 控制台的 "Environment" 頁面新增：
```
RUTEN_API_KEY=your_api_key_here
RUTEN_SECRET_KEY=your_secret_key_here
RUTEN_SALT_KEY=your_salt_key_here
SECRET_KEY=your_flask_secret_key
```

### 5. 部署
點擊 "Create Web Service" 開始部署。部署完成後，Render 會提供一個公開的 URL。

## API 文件

### 認證端點

#### POST /api/auth/verify
驗證 API 金鑰是否有效

**請求參數**:
```json
{
  "api_key": "string",
  "secret_key": "string",
  "salt_key": "string"
}
```

#### GET /api/auth/status
取得目前認證狀態

### 商品管理端點

#### GET /api/products
查詢商品列表

**查詢參數**:
- `page`: 頁碼 (預設: 1)
- `page_size`: 每頁筆數 (預設: 30)
- `status`: 商品狀態 (online|offline|all)

#### POST /api/products
新增商品

#### PUT /api/products/{product_id}
更新商品資訊

#### PUT /api/products/{product_id}/stock
更新商品庫存

#### PUT /api/products/{product_id}/price
更新商品價格

#### PUT /api/products/{product_id}/status
更新商品狀態

#### DELETE /api/products/{product_id}
刪除商品

#### POST /api/products/sync
從露天拍賣同步商品資料

### 訂單管理端點

#### GET /api/orders
查詢訂單列表

#### POST /api/orders/{order_id}/ship
訂單出貨

#### POST /api/orders/{order_id}/cancel
取消訂單

#### POST /api/orders/{order_id}/refund
訂單退款

#### POST /api/orders/sync
從露天拍賣同步訂單資料

### 分類管理端點

#### GET /api/categories
查詢分類列表

#### POST /api/categories
新增分類

#### PUT /api/categories/{category_id}
更新分類

#### DELETE /api/categories/{category_id}
刪除分類

#### POST /api/categories/sync
從露天拍賣同步分類資料

## 資料庫結構

### 商品表 (products)
- `id`: 主鍵
- `ruten_item_id`: 露天商品ID
- `title`: 商品標題
- `description`: 商品描述
- `price`: 價格
- `stock`: 庫存
- `status`: 狀態 (online/offline)
- `category_id`: 分類ID
- `created_at`: 建立時間
- `updated_at`: 更新時間

### 訂單表 (orders)
- `id`: 主鍵
- `ruten_order_id`: 露天訂單ID
- `buyer_name`: 買家姓名
- `total_amount`: 總金額
- `status`: 訂單狀態
- `order_date`: 訂單日期
- `ship_date`: 出貨日期
- `created_at`: 建立時間
- `updated_at`: 更新時間

### 分類表 (categories)
- `id`: 主鍵
- `ruten_category_id`: 露天分類ID
- `name`: 分類名稱
- `parent_id`: 上層分類ID
- `created_at`: 建立時間
- `updated_at`: 更新時間

### API 日誌表 (api_logs)
- `id`: 主鍵
- `endpoint`: API 端點
- `method`: HTTP 方法
- `request_data`: 請求資料
- `response_data`: 回應資料
- `status_code`: 狀態碼
- `execution_time`: 執行時間
- `created_at`: 建立時間

## 使用說明

### 1. 設定 API 憑證
首次使用時，點擊 "設定 API 金鑰" 按鈕，輸入露天拍賣提供的 API 憑證。

### 2. 商品管理
- 點擊 "新增商品" 建立新商品
- 使用 "同步商品" 從露天拍賣匯入現有商品
- 點擊商品列表中的編輯按鈕修改商品資訊

### 3. 訂單處理
- 在訂單管理頁面查看所有訂單
- 點擊 "出貨" 按鈕處理訂單出貨
- 使用 "取消" 按鈕取消訂單

### 4. 分類管理
- 建立商品分類階層
- 設定上下層分類關係
- 與露天拍賣分類保持同步

## 安全性考量

### API 金鑰管理
- 所有敏感資訊透過環境變數管理
- 不在程式碼中硬編碼任何金鑰
- 建議定期輪換 API 金鑰

### 請求驗證
- 實作 HMAC-SHA256 簽章驗證
- 防止 SQL 注入攻擊
- 統一錯誤處理機制

### CORS 設定
- 允許指定網域的跨域請求
- 設定適當的 CORS 標頭

## 效能最佳化

### 資料快取
- 商品資訊本地快取
- 減少 API 請求頻率
- 提升回應速度

### 資料庫最佳化
- 建立適當的索引
- 實作分頁查詢
- 定期清理過期資料

## 故障排除

### 常見問題

#### 1. API 憑證驗證失敗
- 檢查 API Key、Secret Key、Salt Key 是否正確
- 確認時間戳差異在 5 分鐘內
- 檢查網路連線狀態

#### 2. 商品同步失敗
- 確認 API 憑證有效
- 檢查露天拍賣 API 服務狀態
- 查看錯誤日誌詳細資訊

#### 3. 部署問題
- 確認所有環境變數已正確設定
- 檢查 requirements.txt 是否包含所有相依套件
- 查看 Render 部署日誌

### 日誌查看
應用程式會記錄所有 API 請求與回應，可透過資料庫查詢或日誌檔案查看詳細資訊。

## 授權條款

本專案採用 MIT 授權條款。詳細內容請參閱 LICENSE 檔案。

## 技術支援

如有任何問題或建議，請透過以下方式聯繫：
- 建立 GitHub Issue
- 發送電子郵件至專案維護者

## 更新日誌

### v1.0.0 (2025-06-17)
- 初始版本發布
- 完整的商品、訂單、分類管理功能
- 露天拍賣 API 整合
- Render 部署支援
- 現代化前端介面

