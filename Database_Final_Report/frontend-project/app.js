const API_BASE = "http://127.0.0.1:8000/api";

// 簡化 DOM 選擇器
const el = (id) => document.getElementById(id);

let editModalInstance;

// 格式化錯誤訊息
function formatError(detail) {
    if (Array.isArray(detail)) {
        return detail.map(err => `[欄位 ${err.loc[err.loc.length - 1]}] : ${err.msg}`).join('\n');
    } else if (typeof detail === 'object' && detail !== null) {
        return JSON.stringify(detail, null, 2);
    }
    return detail || "未知錯誤";
}

// 取得冰箱清單 (Read) 
async function loadInventory() {
    try {
        const res = await fetch(`${API_BASE}/inventory`);
        const result = await res.json();
        const tbody = el('inventoryTable');
        tbody.innerHTML = '';
        
        if (result.data) {
            const today = new Date();
            
            result.data.forEach(item => {
                // 計算過期時間邏輯
                const expireDate = new Date(item.expire_date);
                const timeDiff = expireDate.getTime() - today.getTime();
                const daysLeft = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
                
                let dateStyle = "";
                let alertBadge = "";
                
                if (daysLeft <= 0) {
                    dateStyle = "text-danger fw-bold table-danger";
                    alertBadge = ' <span class="badge bg-danger">已過期</span>';
                } else if (daysLeft <= 3) {
                    dateStyle = "text-danger fw-bold";
                    alertBadge = ' <span class="badge bg-warning text-dark">即期</span>';
                }

                // 建立表格列
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.name} <small class="text-muted">(${item.category})</small>${alertBadge}</td>
                    <td>${item.quantity} ${item.unit}</td>
                    <td class="${dateStyle}">${item.expire_date}</td>
                    <td>
                        <button class="btn btn-primary btn-sm me-1 action-edit" 
                            data-id="${item.id}" data-name="${item.name}" data-category="${item.category}" 
                            data-qty="${item.quantity}" data-unit="${item.unit}" data-expire="${item.expire_date}">
                            編輯
                        </button>
                        <button class="btn btn-danger btn-sm action-delete" data-id="${item.id}">刪除</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error("載入清單失敗:", error);
    }
}

// 新增食材 (Create)
el('addForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: el('ingName').value.trim(),
        category: el('ingCategory').value.trim(),
        quantity: parseFloat(el('qty').value),
        unit: el('unit').value.trim(),
        expire_date: el('expDate').value
    };

    try {
        const res = await fetch(`${API_BASE}/inventory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            alert(result.message || "新增成功！"); 
            el('addForm').reset(); 
            loadInventory(); 
        } else {
            alert("新增失敗：\n" + formatError(result.detail));
        }
    } catch (error) {
        alert("連線失敗，請檢查後端是否開啟");
    }
});

// 彈窗與修改處理 (Update) 
function openEditModal(btn) {
    el('editId').value = btn.dataset.id;
    el('editName').value = btn.dataset.name;          
    el('editCategory').value = btn.dataset.category;  
    el('editQty').value = btn.dataset.qty;
    el('editUnit').value = btn.dataset.unit;
    el('editExpDate').value = btn.dataset.expire;
    
    if (!editModalInstance) {
        editModalInstance = new bootstrap.Modal(el('editModal'));
    }
    editModalInstance.show();
}

el('submitEditBtn').addEventListener('click', async () => {
    const id = el('editId').value;
    const data = {
        name: el('editName').value.trim(),          
        category: el('editCategory').value.trim(),  
        quantity: parseFloat(el('editQty').value),
        unit: el('editUnit').value.trim(),
        expire_date: el('editExpDate').value
    };

    try {
        const res = await fetch(`${API_BASE}/inventory/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            alert(result.message || "修改成功！");
            editModalInstance.hide(); 
            loadInventory();          
        } else {
            alert("修改失敗：\n" + formatError(result.detail));
        }
    } catch (error) {
        alert("修改連線失敗");
    }
});

// 刪除食材 (Delete) 
async function deleteItem(id) {
    if (!confirm('確定要移除這項食材嗎？')) return;
    try {
        const res = await fetch(`${API_BASE}/inventory/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadInventory();
        }
    } catch (error) {
        alert("刪除失敗");
    }
}

// 事件委派
el('inventoryTable').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    
    if (btn.classList.contains('action-edit')) {
        openEditModal(btn);
    } else if (btn.classList.contains('action-delete')) {
        deleteItem(btn.dataset.id);
    }
});

// 智慧推薦 (演算法)
async function getSmartRecommend() {
    const res = await fetch(`${API_BASE}/recipes/smart-recommend`);
    const result = await res.json();
    const div = el('smartRecommendList');
    div.innerHTML = '';

    if (!result.data || result.data.length === 0) {
        div.innerHTML = '<p class="text-success">目前沒有即將過期的食材。</p>';
        return;
    }

    result.data.forEach(r => {
        div.innerHTML += `
            <div class="mb-3 border-bottom pb-2">
                <strong>🍴 ${r[0]}</strong> <span class="badge bg-danger float-end">清掉 ${r[2]} 樣</span>
                <br><small class="text-muted">${r[1] || ''}</small>
            </div>
        `;
    });
}

el('smartRecommendBtn').addEventListener('click', getSmartRecommend);
el('refreshInventoryBtn').addEventListener('click', loadInventory);

// 載入所有食譜
async function loadRecipes() {
    try {
        const res = await fetch(`${API_BASE}/recipes/recommend`);
        const result = await res.json();
        const div = el('allRecipeList');
        div.innerHTML = '';
        
        if (result.data) {
            result.data.forEach(r => {
                let ingText = r.ingredients.map(i => `${i.item} ${i.qty}${i.unit}`).join(', ');
                div.innerHTML += `
                    <div class="col-md-6 mb-2">
                        <div class="p-2 border rounded bg-white">
                            <h6>${r.name}</h6>
                            <small class="text-muted">材料：${ingText}</small>
                        </div>
                    </div>
                `;
            });
        }
    } catch (error) {
        console.error("載入食譜失敗:", error);
    }
}

// 初始化
window.addEventListener("DOMContentLoaded", () => {
    loadInventory();
    loadRecipes();
});