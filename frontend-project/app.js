const API_BASE = "http://127.0.0.1:8000/api";

// 簡化 DOM 選擇器
const el = (id) => document.getElementById(id);

// 全域變數
let editModalInstance;
let recipeModalInstance;
let allRecipesData = [];

// 格式化錯誤訊息
function formatError(detail) {
    if (Array.isArray(detail)) {
        return detail.map(err => `[欄位 ${err.loc[err.loc.length - 1]}] : ${err.msg}`).join('\n');
    } else if (typeof detail === 'object' && detail !== null) {
        return JSON.stringify(detail, null, 2);
    }
    return detail || "未知錯誤";
}

// ================= 冰箱庫存區塊 =================

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

// 食材清單表格事件委派 (處理編輯與刪除按鈕)
el('inventoryTable').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    
    if (btn.classList.contains('action-edit')) {
        openEditModal(btn);
    } else if (btn.classList.contains('action-delete')) {
        deleteItem(btn.dataset.id);
    }
});

// ================= 智慧推薦與食譜區塊 =================

// 智慧推薦
async function getSmartRecommend() {
    try {
        const res = await fetch(`${API_BASE}/recipes/smart-recommend`);
        const result = await res.json();
        const div = el('smartRecommendList');
        div.innerHTML = '';

        if (!result.data || result.data.length === 0) {
            div.innerHTML = '<p class="text-muted">太棒了！目前沒有即將過期的食材。</p>';
            return;
        }

        result.data.forEach(r => {
            div.innerHTML += `
                <div class="mb-3 border-bottom pb-2">
                    <strong>🍴 ${r.recipe_name}</strong> 
                    <span class="badge badge-emergency float-end">清掉 ${r.emergency_count} 樣</span>
                    <br><small class="text-muted">${r.description || ''}</small>
                </div>
            `;
        });
    } catch (error) {
        console.error("載入智慧推薦失敗", error);
    }
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
            allRecipesData = result.data; // 儲存供編輯時使用
            result.data.forEach(r => {
                let ingText = r.ingredients ? r.ingredients.map(i => `${i.item} ${i.qty}${i.unit}`).join(', ') : '無';
                div.innerHTML += `
                    <div class="col-md-6 mb-3">
                        <div class="p-3 border rounded bg-white shadow-sm h-100 d-flex flex-column">
                            <h6 class="fw-bold">${r.name}</h6>
                            <small class="text-muted mb-2">${r.description || '無描述'}</small>
                            <small class="text-dark flex-grow-1"><strong>材料：</strong>${ingText}</small>
                            <div class="d-flex justify-content-end mt-2">
                                <button class="btn btn-primary btn-sm me-1" onclick="openRecipeModal(${r.id})">編輯</button>
                                <button class="btn btn-danger btn-sm" onclick="deleteRecipe(${r.id})">刪除</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (error) {
        console.error("載入食譜失敗:", error);
    }
}

// 動態新增一列食材輸入框 (對外曝露給 HTML onclick 使用)
window.addRecipeIngredientRow = function(name = '', qty = '', unit = '') {
    const container = el('recipeIngredientsContainer');
    const row = document.createElement('div');
    row.className = 'row mb-2 recipe-ing-row';
    row.innerHTML = `
        <div class="col-5">
            <input type="text" class="form-control ing-name" placeholder="食材名稱" value="${name}" required>
        </div>
        <div class="col-3">
            <input type="number" step="0.1" class="form-control ing-qty" placeholder="數量" value="${qty}" required>
        </div>
        <div class="col-3">
            <input type="text" class="form-control ing-unit" placeholder="單位" value="${unit}" required>
        </div>
        <div class="col-1 d-flex align-items-center">
            <button type="button" class="btn btn-danger btn-sm w-100" onclick="this.parentElement.parentElement.remove()">X</button>
        </div>
    `;
    container.appendChild(row);
}

// 開啟新增/修改食譜的 Modal
window.openRecipeModal = function(recipeId = null) {
    const isEdit = recipeId !== null;
    el('recipeModalTitle').innerText = isEdit ? '修改食譜' : '新增食譜';
    el('recipeId').value = isEdit ? recipeId : '';
    el('recipeIngredientsContainer').innerHTML = '';

    if (isEdit) {
        // 找出對應的食譜資料並填入
        const recipe = allRecipesData.find(r => r.id === recipeId);
        el('recipeName').value = recipe.name;
        el('recipeDesc').value = recipe.description || '';
        
        if (recipe.ingredients && recipe.ingredients.length > 0) {
            recipe.ingredients.forEach(i => addRecipeIngredientRow(i.item, i.qty, i.unit));
        } else {
            addRecipeIngredientRow();
        }
    } else {
        // 清空表單，給一個預設的空白食材列
        el('recipeName').value = '';
        el('recipeDesc').value = '';
        addRecipeIngredientRow(); 
    }

    if (!recipeModalInstance) {
        recipeModalInstance = new bootstrap.Modal(el('recipeModal'));
    }
    recipeModalInstance.show();
}

// 送出食譜 (包含新增與修改)
window.submitRecipe = async function() {
    const id = el('recipeId').value;
    const name = el('recipeName').value.trim();
    const description = el('recipeDesc').value.trim();
    
    // 抓取所有動態產生的食材資料
    const rows = document.querySelectorAll('.recipe-ing-row');
    const ingredients = Array.from(rows).map(row => ({
        name: row.querySelector('.ing-name').value,
        category: "未分類", 
        quantity: parseFloat(row.querySelector('.ing-qty').value),
        unit: row.querySelector('.ing-unit').value
    }));

    if (!name || ingredients.length === 0) {
        alert("請填寫食譜名稱並至少加入一項食材！");
        return;
    }

    const data = { name, description, ingredients };
    const isEdit = id !== '';
    const url = isEdit ? `${API_BASE}/recipes/${id}` : `${API_BASE}/recipes`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (res.ok) {
            alert(result.message || "食譜儲存成功！");
            recipeModalInstance.hide();
            loadRecipes();
        } else {
            alert("儲存失敗：\n" + formatError(result.detail));
        }
    } catch (error) {
        alert("連線失敗，請檢查後端是否開啟");
    }
}

// 刪除食譜
window.deleteRecipe = async function(id) {
    if (!confirm('確定要刪除這項食譜嗎？')) return;
    try {
        const res = await fetch(`${API_BASE}/recipes/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadRecipes();
        } else {
            const result = await res.json();
            alert("刪除失敗: " + formatError(result.detail));
        }
    } catch (error) {
        alert("刪除失敗，請檢查網路連線");
    }
}

// 初始載入
window.addEventListener("DOMContentLoaded", () => {
    loadInventory();
    loadRecipes();
});
