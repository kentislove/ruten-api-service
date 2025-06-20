# 露天拍賣 API 管理系統 - 部署指南

## 快速部署到 Render

### 步驟 1: 準備專案檔案

確保您的專案包含以下檔案：
- `Procfile` - Render 部署配置
- `requirements.txt` - Python 相依套件
- `runtime.txt` - Python 版本指定
- `src/main.py` - Flask 應用程式主檔案

### 步驟 2: 建立 GitHub 儲存庫

1. 在 GitHub 建立新的儲存庫
2. 將專案檔案推送到儲存庫：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/ruten-api-service.git
git push -u origin main
```

### 步驟 3: 在 Render 建立 Web Service

1. 前往 [Render Dashboard](https://dashboard.render.com/)
2. 點擊 "New +" 按鈕
3. 選擇 "Web Service"
4. 連接您的 GitHub 帳號
5. 選擇 `ruten-api-service` 儲存庫

### 步驟 4: 配置服務設定

在 Render 的服務配置頁面設定：

**基本設定**
- **Name**: `ruten-api-service`
- **Environment**: `Python 3`
- **Region**: 選擇最近的區域
- **Branch**: `main`

**建置設定**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`

### 步驟 5: 設定環境變數

在 "Environment" 頁面新增以下環境變數：

```
RUTEN_API_KEY=your_api_key_here
RUTEN_SECRET_KEY=your_secret_key_here
RUTEN_SALT_KEY=your_salt_key_here
SECRET_KEY=your_flask_secret_key_here
```

**重要提醒**：
- 請將 `your_api_key_here` 等替換為實際的露天拍賣 API 憑證
- `SECRET_KEY` 請使用隨機生成的安全金鑰

### 步驟 6: 部署服務

1. 點擊 "Create Web Service" 開始部署
2. 等待部署完成（通常需要 3-5 分鐘）
3. 部署成功後，Render 會提供一個公開的 URL

### 步驟 7: 驗證部署

1. 開啟 Render 提供的 URL
2. 確認網頁正常載入
3. 測試 API 金鑰設定功能
4. 驗證各項功能運作正常

## 環境變數詳細說明

### 必要環境變數

| 變數名稱 | 說明 | 範例 |
|---------|------|------|
| `RUTEN_API_KEY` | 露天拍賣 API 金鑰 | `axx9dbiee3vh4r4we5axabeyer196zsj` |
| `RUTEN_SECRET_KEY` | 露天拍賣 Secret 金鑰 | `your_secret_key` |
| `RUTEN_SALT_KEY` | 露天拍賣 Salt 金鑰 | `your_salt_key` |
| `SECRET_KEY` | Flask 應用程式密鑰 | `your_random_secret_key` |

### 可選環境變數

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| `DATABASE_URL` | 資料庫連線 URL | `sqlite:///app.db` |
| `FLASK_ENV` | Flask 環境模式 | `production` |

## 取得露天拍賣 API 憑證

### 申請步驟

1. 登入露天拍賣賣家中心
2. 前往「API 管理」頁面
3. 申請開發者權限
4. 建立新的 API 應用程式
5. 取得 API Key、Secret Key 和 Salt Key

### 權限設定

確保您的 API 應用程式具有以下權限：
- 商品管理權限
- 訂單管理權限
- 分類管理權限

## 自訂網域設定（可選）

如果您想使用自訂網域：

1. 在 Render 服務設定中點擊 "Custom Domains"
2. 新增您的網域名稱
3. 在您的 DNS 提供商設定 CNAME 記錄
4. 等待 SSL 憑證自動配置完成

## 監控與維護

### 查看日誌

1. 在 Render Dashboard 中選擇您的服務
2. 點擊 "Logs" 頁面查看即時日誌
3. 使用日誌排查問題

### 效能監控

Render 提供基本的效能監控：
- CPU 使用率
- 記憶體使用量
- 回應時間
- 錯誤率

### 自動部署

當您推送新的程式碼到 GitHub 主分支時，Render 會自動重新部署您的應用程式。

## 故障排除

### 常見部署問題

#### 1. 建置失敗
**症狀**: 部署過程中出現套件安裝錯誤
**解決方案**:
- 檢查 `requirements.txt` 格式是否正確
- 確認所有套件版本相容
- 查看建置日誌中的詳細錯誤訊息

#### 2. 應用程式無法啟動
**症狀**: 部署成功但服務無法存取
**解決方案**:
- 檢查 `Procfile` 中的啟動命令
- 確認環境變數設定正確
- 查看應用程式日誌

#### 3. 資料庫連線問題
**症狀**: 應用程式啟動但功能異常
**解決方案**:
- 檢查資料庫檔案權限
- 確認 SQLite 資料庫路徑正確
- 查看資料庫相關錯誤訊息

#### 4. API 憑證驗證失敗
**症狀**: 無法連接露天拍賣 API
**解決方案**:
- 確認環境變數中的 API 憑證正確
- 檢查 API 憑證是否已過期
- 驗證 API 權限設定

### 效能最佳化建議

#### 1. 資料庫最佳化
- 定期清理過期的 API 日誌
- 為常用查詢欄位建立索引
- 實作資料分頁避免大量資料載入

#### 2. API 請求最佳化
- 實作請求快取機制
- 批次處理多筆資料更新
- 設定適當的請求重試邏輯

#### 3. 前端最佳化
- 壓縮 CSS 和 JavaScript 檔案
- 使用 CDN 載入外部資源
- 實作前端快取策略

## 安全性最佳實務

### 1. 環境變數管理
- 絕不在程式碼中硬編碼敏感資訊
- 定期輪換 API 金鑰
- 使用強密碼作為 Flask SECRET_KEY

### 2. API 安全
- 實作請求頻率限制
- 記錄所有 API 請求以供稽核
- 監控異常的 API 使用模式

### 3. 資料保護
- 定期備份重要資料
- 實作資料加密（如需要）
- 遵循資料保護法規

## 擴展功能建議

### 1. 使用者認證
- 實作多使用者支援
- 新增角色權限管理
- 整合第三方認證服務

### 2. 進階功能
- 新增商品圖片上傳功能
- 實作庫存預警通知
- 建立銷售報表分析

### 3. 整合服務
- 串接其他電商平台 API
- 整合物流追蹤服務
- 連接會計軟體

## 技術支援

如遇到部署或使用問題，請參考：

1. **Render 官方文件**: https://render.com/docs
2. **Flask 官方文件**: https://flask.palletsprojects.com/
3. **露天拍賣 API 文件**: 請參考露天拍賣開發者中心

## 費用說明

### Render Free Plan 限制
- 每月 750 小時免費使用時間
- 服務閒置 15 分鐘後會進入睡眠狀態
- 記憶體限制 512MB
- 無自訂網域支援

### 升級建議
如需更穩定的服務，建議升級到 Render 付費方案：
- 無睡眠限制
- 更多記憶體和 CPU 資源
- 自訂網域支援
- 優先技術支援

---

**部署完成後，您就擁有一個功能完整的露天拍賣管理系統！**

