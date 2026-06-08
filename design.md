## API 設計

## 冰箱食材管理

### 1. 取得冰箱所有食材
*   端點: `GET /api/inventory`
*   參數: N/A
*   狀態碼: `200 OK`
*   回應: Object
*       回應欄位
*           status: str
*           data: Array

id: int

name: str

category: str

quantity: float

unit: str

expire_date: str (yyyy-mm-dd)

回應範例

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

## 2. 新增食材到冰箱

端點: `POST /api/inventory`

參數:

name: str (必填)

category: str (必填)

quantity: float (必填)

unit: str (必填)

expire_date: str (yyyy-mm-dd) (必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

db_id: int

回應範例

```json
{
    "status": "success",
    "message": "食材 '高麗菜' 已存入冰箱",
    "db_id": 1
}
```

## 3. 修改冰箱裡的食材

端點: `PUT /api/inventory/{item_id}`

參數:

item_id: int (Path，必填)

name: str (必填)

category: str (必填)

quantity: float (必填)

unit: str (必填)

expire_date: str (yyyy-mm-dd) (必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

回應範例

```json
{
    "status": "success",
    "message": "食材修改成功！名稱已更新為 '高麗菜'"
}
```

找不到時回傳 404

```json
{
    "detail": "找不到這筆食材"
}
```

## 4. 從冰箱刪除食材

端點: `DELETE /api/inventory/{item_id}`

參數:

item_id: int (Path，必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

回應範例

```json
{
    "status": "success",
    "message": "食材 ID 1 已經刪除"
}
```

找不到時回傳 404

```json
{
    "detail": "找不到這筆食材"
}
```

---

# 冰箱食譜管理

## 1. 取得所有食譜清單

端點: `GET /api/recipes/recommend`

參數: N/A

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

data: Array

id: int

name: str

description: str

ingredients: Array

item: str

qty: float

unit: str

回應範例

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
                },
                {
                    "item": "雞蛋",
                    "qty": 3.0,
                    "unit": "顆"
                }
            ]
        }
    ]
}
```

## 2. 新增食譜

端點: `POST /api/recipes`

參數:

name: str (必填)

description: str (選填，預設為 "")

ingredients: Array (必填)

ingredients 物件欄位

name: str (必填)

category: str (選填，預設為 "未分類")

quantity: float (必填)

unit: str (必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

recipe_id: int

回應範例

```json
{
    "status": "success",
    "message": "食譜 '番茄炒蛋' 新增成功！",
    "recipe_id": 1
}
```

## 3. 修改食譜

端點: `PUT /api/recipes/{recipe_id}`

參數:

recipe_id: int (Path，必填)

name: str (必填)

description: str (選填，預設為 "")

ingredients: Array (必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

回應範例

```json
{
    "status": "success",
    "message": "食譜 '番茄炒蛋' 修改成功！"
}
```

找不到時回傳 404

```json
{
    "detail": "找不到此食譜"
}
```

## 4. 刪除食譜

端點: `DELETE /api/recipes/{recipe_id}`

參數:

recipe_id: int (Path，必填)

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

message: str

回應範例

```json
{
    "status": "success",
    "message": "食譜已刪除！"
}
```

找不到時回傳 404

```json
{
    "detail": "找不到此食譜"
}
```

## 5. 智慧推薦食譜

端點: `GET /api/recipes/smart-recommend`

參數: N/A

狀態碼: `200 OK`

回應: Object

回應欄位

status: str

algorithm: str

data: Array

recipe_name: str

description: str

emergency_count: int

回應範例

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
