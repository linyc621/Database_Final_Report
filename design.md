# 冰箱食材管理 API

## 1. 取得冰箱所有食材

### Endpoint
```http
GET /api/inventory
```

### 參數
無

### Response

**Status Code:** `200 OK`

| 欄位 | 型別 | 說明 |
|--------|--------|--------|
| id | int | 食材 ID |
| name | string | 食材名稱 |
| category | string | 食材分類 |
| quantity | float | 數量 |
| unit | string | 單位 |
| expire_date | string | 到期日 (yyyy-mm-dd) |

### 回應範例

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "高麗菜",
      "category": "蔬菜",
      "quantity": 0.5,
      "unit": "顆",
      "expire_date": "2026-06-15"
    }
  ]
}
```

---

## 2. 新增食材到冰箱

### Endpoint

```http
POST /api/inventory
```

### Request Body

| 欄位 | 型別 | 必填 | 說明 |
|--------|--------|--------|--------|
| name | string | ✓ | 食材名稱 |
| category | string | ✓ | 食材分類 |
| quantity | float | ✓ | 數量 |
| unit | string | ✓ | 單位 |
| expire_date | string | ✓ | 到期日 (yyyy-mm-dd) |

### Response

**Status Code:** `200 OK`

| 欄位 | 型別 |
|--------|--------|
| status | string |
| message | string |
| db_id | int |

### 回應範例

```json
{
  "status": "success",
  "message": "食材 '高麗菜' 已存入冰箱",
  "db_id": 1
}
```

---

## 3. 修改冰箱裡的食材

### Endpoint

```http
PUT /api/inventory/{item_id}
```

### Path Parameter

| 參數 | 型別 | 必填 |
|--------|--------|--------|
| item_id | int | ✓ |

### Request Body

| 欄位 | 型別 | 必填 |
|--------|--------|--------|
| quantity | float | ✓ |
| unit | string | ✓ |
| expire_date | string | ✓ |

### Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "食材修改成功！"
}
```

### 錯誤回應

**Status Code:** `404 Not Found`

```json
{
  "status": "error",
  "message": "找不到指定食材"
}
```

---

## 4. 刪除冰箱食材

### Endpoint

```http
DELETE /api/inventory/{item_id}
```

### Path Parameter

| 參數 | 型別 | 必填 |
|--------|--------|--------|
| item_id | int | ✓ |

### Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "食材 ID 1 已經刪除"
}
```

### 錯誤回應

**Status Code:** `404 Not Found`

```json
{
  "status": "error",
  "message": "找不到指定食材"
}
```

---

# 冰箱食譜管理 API

## 5. 取得所有推薦食譜

### Endpoint

```http
GET /api/recipes/recommend
```

### 參數

無

### Response

**Status Code:** `200 OK`

| 欄位 | 型別 |
|--------|--------|
| status | string |
| data | array |

### 回應範例

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "番茄炒蛋",
      "description": "經典清冰箱家常菜",
      "ingredients": [
        {
          "item": "番茄",
          "qty": 2.0,
          "unit": "顆"
        }
      ]
    }
  ]
}
```

---

## 6. 新增食譜

### Endpoint

```http
POST /api/recipes
```

### Request Body

| 欄位 | 型別 | 必填 |
|--------|--------|--------|
| name | string | ✓ |
| description | string | ✗ |
| ingredients | array | ✓ |

### ingredients 格式

```json
[
  {
    "name": "番茄",
    "category": "蔬菜",
    "quantity": 2,
    "unit": "顆"
  }
]
```

### Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "食譜 '番茄炒蛋' 新增成功！",
  "recipe_id": 1
}
```

---

## 7. 修改食譜

### Endpoint

```http
PUT /api/recipes/{recipe_id}
```

### Path Parameter

| 參數 | 型別 | 必填 |
|--------|--------|--------|
| recipe_id | int | ✓ |

### Request Body

| 欄位 | 型別 | 必填 |
|--------|--------|--------|
| name | string | ✓ |
| description | string | ✗ |
| ingredients | array | ✓ |

### Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "食譜 '番茄炒蛋' 修改成功！"
}
```

### 錯誤回應

**Status Code:** `404 Not Found`

```json
{
  "status": "error",
  "message": "找不到指定食譜"
}
```

---

## 8. 刪除食譜

### Endpoint

```http
DELETE /api/recipes/{recipe_id}
```

### Path Parameter

| 參數 | 型別 | 必填 |
|--------|--------|--------|
| recipe_id | int | ✓ |

### Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "食譜已刪除！"
}
```

### 錯誤回應

**Status Code:** `404 Not Found`

```json
{
  "status": "error",
  "message": "找不到指定食譜"
}
```

---

# 智慧推薦食譜 API

## 9. 智慧推薦食譜

### Endpoint

```http
GET /api/recipes/smart-recommend
```

### 參數

無

### Response

**Status Code:** `200 OK`

| 欄位 | 型別 |
|--------|--------|
| status | string |
| algorithm | string |
| data | array |

### 回應範例

```json
{
  "status": "success",
  "algorithm": "Greedy (Expiring First)",
  "data": [
    {
      "recipe_name": "番茄炒蛋",
      "description": "經典清冰箱家常菜",
      "emergency_count": 2
    }
  ]
}
```
