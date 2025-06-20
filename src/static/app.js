// 全域變數
let currentPage = 1;
let currentTab = 'products';
let apiBaseUrl = window.location.origin;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    loadProducts();
    
    // 設定表單提交事件
    document.getElementById('authForm').addEventListener('submit', handleAuthSubmit);
    document.getElementById('productForm').addEventListener('submit', handleProductSubmit);
    document.getElementById('categoryForm').addEventListener('submit', handleCategorySubmit);
});

// 檢查認證狀態
async function checkAuthStatus() {
    try {
        const response = await fetch(`${apiBaseUrl}/api/auth/status`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const data = result.data;
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (data.has_credentials && data.credentials_valid) {
                statusDot.classList.add('connected');
                statusText.textContent = `已連線 (${data.api_key_preview})`;
            } else if (data.has_credentials) {
                statusText.textContent = '憑證無效，請重新設定';
            } else {
                statusText.textContent = '未設定 API 憑證';
            }
        }
    } catch (error) {
        console.error('檢查認證狀態失敗:', error);
        document.getElementById('statusText').textContent = '連線失敗';
    }
}

// 顯示/隱藏模態框
function showAuthModal() {
    document.getElementById('authModal').classList.add('show');
}

function hideAuthModal() {
    document.getElementById('authModal').classList.remove('show');
}

function showProductModal(product = null) {
    const modal = document.getElementById('productModal');
    const title = document.getElementById('productModalTitle');
    const form = document.getElementById('productForm');
    
    if (product) {
        title.innerHTML = '<i class="fas fa-edit"></i> 編輯商品';
        document.getElementById('productId').value = product.id;
        document.getElementById('productTitle').value = product.title;
        document.getElementById('productDescription').value = product.description || '';
        document.getElementById('productPrice').value = product.price;
        document.getElementById('productStock').value = product.stock;
        document.getElementById('productStatus').value = product.status;
    } else {
        title.innerHTML = '<i class="fas fa-plus"></i> 新增商品';
        form.reset();
        document.getElementById('productId').value = '';
    }
    
    modal.classList.add('show');
}

function hideProductModal() {
    document.getElementById('productModal').classList.remove('show');
}

function showCategoryModal(category = null) {
    const modal = document.getElementById('categoryModal');
    const title = document.getElementById('categoryModalTitle');
    const form = document.getElementById('categoryForm');
    
    if (category) {
        title.innerHTML = '<i class="fas fa-edit"></i> 編輯分類';
        document.getElementById('categoryId').value = category.id;
        document.getElementById('categoryName').value = category.name;
        document.getElementById('categoryParent').value = category.parent_id || '';
    } else {
        title.innerHTML = '<i class="fas fa-plus"></i> 新增分類';
        form.reset();
        document.getElementById('categoryId').value = '';
    }
    
    modal.classList.add('show');
}

function hideCategoryModal() {
    document.getElementById('categoryModal').classList.remove('show');
}

// 切換分頁
function showTab(tabName) {
    // 隱藏所有分頁內容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有分頁按鈕的 active 類別
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 顯示選中的分頁
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    currentTab = tabName;
    currentPage = 1;
    
    // 載入對應的資料
    switch(tabName) {
        case 'products':
            loadProducts();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'categories':
            loadCategories();
            break;
    }
}

// 處理認證表單提交
async function handleAuthSubmit(event) {
    event.preventDefault();
    
    const apiKey = document.getElementById('apiKey').value;
    const secretKey = document.getElementById('secretKey').value;
    const saltKey = document.getElementById('saltKey').value;
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey,
                secret_key: secretKey,
                salt_key: saltKey
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success' && result.data.valid) {
            showAlert('success', '憑證驗證成功！');
            hideAuthModal();
            checkAuthStatus();
        } else {
            showAlert('danger', `憑證驗證失敗: ${result.data.message}`);
        }
    } catch (error) {
        showAlert('danger', `驗證失敗: ${error.message}`);
    }
}

// 處理商品表單提交
async function handleProductSubmit(event) {
    event.preventDefault();
    
    const productId = document.getElementById('productId').value;
    const productData = {
        title: document.getElementById('productTitle').value,
        description: document.getElementById('productDescription').value,
        price: parseFloat(document.getElementById('productPrice').value),
        stock: parseInt(document.getElementById('productStock').value),
        status: document.getElementById('productStatus').value
    };
    
    try {
        let response;
        if (productId) {
            // 更新商品
            response = await fetch(`${apiBaseUrl}/api/products/${productId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
        } else {
            // 新增商品
            response = await fetch(`${apiBaseUrl}/api/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', productId ? '商品更新成功！' : '商品新增成功！');
            hideProductModal();
            loadProducts();
        } else {
            showAlert('danger', `操作失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `操作失敗: ${error.message}`);
    }
}

// 處理分類表單提交
async function handleCategorySubmit(event) {
    event.preventDefault();
    
    const categoryId = document.getElementById('categoryId').value;
    const categoryData = {
        name: document.getElementById('categoryName').value,
        parent_id: document.getElementById('categoryParent').value || null
    };
    
    try {
        let response;
        if (categoryId) {
            // 更新分類
            response = await fetch(`${apiBaseUrl}/api/categories/${categoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });
        } else {
            // 新增分類
            response = await fetch(`${apiBaseUrl}/api/categories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', categoryId ? '分類更新成功！' : '分類新增成功！');
            hideCategoryModal();
            loadCategories();
        } else {
            showAlert('danger', `操作失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `操作失敗: ${error.message}`);
    }
}

// 載入商品資料
async function loadProducts(page = 1) {
    const container = document.getElementById('productsContent');
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i><p>載入商品資料中...</p></div>';
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/products?page=${page}&page_size=10`);
        const result = await response.json();
        
        if (result.status === 'success') {
            renderProductsTable(result.data);
        } else {
            container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${error.message}</div>`;
    }
}

// 載入訂單資料
async function loadOrders(page = 1) {
    const container = document.getElementById('ordersContent');
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i><p>載入訂單資料中...</p></div>';
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/orders?page=${page}&page_size=10`);
        const result = await response.json();
        
        if (result.status === 'success') {
            renderOrdersTable(result.data);
        } else {
            container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${error.message}</div>`;
    }
}

// 載入分類資料
async function loadCategories() {
    const container = document.getElementById('categoriesContent');
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i><p>載入分類資料中...</p></div>';
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/categories`);
        const result = await response.json();
        
        if (result.status === 'success') {
            renderCategoriesTable(result.data);
            updateCategoryParentOptions(result.data.categories);
        } else {
            container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> 載入失敗: ${error.message}</div>`;
    }
}

// 渲染商品表格
function renderProductsTable(data) {
    const container = document.getElementById('productsContent');
    
    if (data.products.length === 0) {
        container.innerHTML = '<div class="alert alert-warning"><i class="fas fa-info-circle"></i> 目前沒有商品資料</div>';
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>商品標題</th>
                    <th>價格</th>
                    <th>庫存</th>
                    <th>狀態</th>
                    <th>建立時間</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.products.forEach(product => {
        const statusClass = product.status === 'online' ? 'status-online' : 'status-offline';
        const statusText = product.status === 'online' ? '上架' : '下架';
        const createdAt = new Date(product.created_at).toLocaleDateString('zh-TW');
        
        html += `
            <tr>
                <td>${product.id}</td>
                <td>${product.title}</td>
                <td>NT$ ${product.price}</td>
                <td>${product.stock}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${createdAt}</td>
                <td>
                    <button class="btn btn-primary" onclick="showProductModal(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteProduct(${product.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    // 加入分頁
    if (data.pages > 1) {
        html += renderPagination(data.page, data.pages, 'loadProducts');
    }
    
    container.innerHTML = html;
}

// 渲染訂單表格
function renderOrdersTable(data) {
    const container = document.getElementById('ordersContent');
    
    if (data.orders.length === 0) {
        container.innerHTML = '<div class="alert alert-warning"><i class="fas fa-info-circle"></i> 目前沒有訂單資料</div>';
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>買家</th>
                    <th>總金額</th>
                    <th>狀態</th>
                    <th>訂單日期</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.orders.forEach(order => {
        const statusClass = getOrderStatusClass(order.status);
        const orderDate = order.order_date ? new Date(order.order_date).toLocaleDateString('zh-TW') : '-';
        
        html += `
            <tr>
                <td>${order.id}</td>
                <td>${order.buyer_name || '-'}</td>
                <td>NT$ ${order.total_amount || 0}</td>
                <td><span class="status-badge ${statusClass}">${order.status}</span></td>
                <td>${orderDate}</td>
                <td>
                    <button class="btn btn-primary" onclick="shipOrder(${order.id})">
                        <i class="fas fa-shipping-fast"></i> 出貨
                    </button>
                    <button class="btn btn-danger" onclick="cancelOrder(${order.id})">
                        <i class="fas fa-times"></i> 取消
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    // 加入分頁
    if (data.pages > 1) {
        html += renderPagination(data.page, data.pages, 'loadOrders');
    }
    
    container.innerHTML = html;
}

// 渲染分類表格
function renderCategoriesTable(data) {
    const container = document.getElementById('categoriesContent');
    
    if (data.categories.length === 0) {
        container.innerHTML = '<div class="alert alert-warning"><i class="fas fa-info-circle"></i> 目前沒有分類資料</div>';
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>分類名稱</th>
                    <th>上層分類</th>
                    <th>建立時間</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.categories.forEach(category => {
        const createdAt = new Date(category.created_at).toLocaleDateString('zh-TW');
        const parentName = getParentCategoryName(category.parent_id, data.categories);
        
        html += `
            <tr>
                <td>${category.id}</td>
                <td>${category.name}</td>
                <td>${parentName}</td>
                <td>${createdAt}</td>
                <td>
                    <button class="btn btn-primary" onclick="showCategoryModal(${JSON.stringify(category).replace(/"/g, '&quot;')})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteCategory(${category.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// 渲染分頁
function renderPagination(currentPage, totalPages, functionName) {
    let html = '<div class="pagination">';
    
    // 上一頁按鈕
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="${functionName}(${currentPage - 1})">
        <i class="fas fa-chevron-left"></i>
    </button>`;
    
    // 頁碼按鈕
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<button class="active">${i}</button>`;
        } else {
            html += `<button onclick="${functionName}(${i})">${i}</button>`;
        }
    }
    
    // 下一頁按鈕
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="${functionName}(${currentPage + 1})">
        <i class="fas fa-chevron-right"></i>
    </button>`;
    
    html += '</div>';
    return html;
}

// 同步功能
async function syncProducts() {
    try {
        showAlert('warning', '正在同步商品資料...');
        const response = await fetch(`${apiBaseUrl}/api/products/sync`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', `成功同步 ${result.data.synced_count} 個商品`);
            loadProducts();
        } else {
            showAlert('danger', `同步失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `同步失敗: ${error.message}`);
    }
}

async function syncOrders() {
    try {
        showAlert('warning', '正在同步訂單資料...');
        const response = await fetch(`${apiBaseUrl}/api/orders/sync`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', `成功同步 ${result.data.synced_count} 個訂單`);
            loadOrders();
        } else {
            showAlert('danger', `同步失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `同步失敗: ${error.message}`);
    }
}

async function syncCategories() {
    try {
        showAlert('warning', '正在同步分類資料...');
        const response = await fetch(`${apiBaseUrl}/api/categories/sync`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', `成功同步 ${result.data.synced_count} 個分類`);
            loadCategories();
        } else {
            showAlert('danger', `同步失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `同步失敗: ${error.message}`);
    }
}

// 刪除功能
async function deleteProduct(productId) {
    if (!confirm('確定要刪除這個商品嗎？')) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/products/${productId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', '商品刪除成功！');
            loadProducts();
        } else {
            showAlert('danger', `刪除失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `刪除失敗: ${error.message}`);
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('確定要刪除這個分類嗎？')) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/categories/${categoryId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', '分類刪除成功！');
            loadCategories();
        } else {
            showAlert('danger', `刪除失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `刪除失敗: ${error.message}`);
    }
}

// 訂單操作
async function shipOrder(orderId) {
    const trackingNumber = prompt('請輸入追蹤號碼（可選）:');
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/orders/${orderId}/ship`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tracking_number: trackingNumber || ''
            })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', '訂單出貨成功！');
            loadOrders();
        } else {
            showAlert('danger', `出貨失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `出貨失敗: ${error.message}`);
    }
}

async function cancelOrder(orderId) {
    const reason = prompt('請輸入取消原因:');
    if (!reason) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/api/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: reason
            })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('success', '訂單取消成功！');
            loadOrders();
        } else {
            showAlert('danger', `取消失敗: ${result.message}`);
        }
    } catch (error) {
        showAlert('danger', `取消失敗: ${error.message}`);
    }
}

// 輔助函數
function getOrderStatusClass(status) {
    switch(status) {
        case 'shipped': return 'status-shipped';
        case 'pending': return 'status-pending';
        case 'cancelled': return 'status-offline';
        default: return 'status-pending';
    }
}

function getParentCategoryName(parentId, categories) {
    if (!parentId) return '-';
    const parent = categories.find(cat => cat.id === parentId);
    return parent ? parent.name : '-';
}

function updateCategoryParentOptions(categories) {
    const select = document.getElementById('categoryParent');
    select.innerHTML = '<option value="">無上層分類</option>';
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function showAlert(type, message) {
    // 移除現有的警告
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 建立新的警告
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    
    let icon;
    switch(type) {
        case 'success': icon = 'fas fa-check-circle'; break;
        case 'danger': icon = 'fas fa-exclamation-triangle'; break;
        case 'warning': icon = 'fas fa-info-circle'; break;
        default: icon = 'fas fa-info-circle';
    }
    
    alert.innerHTML = `<i class="${icon}"></i> ${message}`;
    
    // 插入到容器頂部
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // 3秒後自動移除
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

