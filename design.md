# Smart Pantry API Design

## Inventory Management

### Get All Ingredients

取得冰箱所有食材。

**Endpoint**

```
GET /api/inventory
```

**Parameters**

N/A

**Response**

Status Code: `200 OK`

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

### Add Ingredient

新增食材到冰箱。

**Endpoint**

```
POST /api/inventory
```

**Request Body**

| Field       | Type                | Required |
| ----------- | ------------------- | -------- |
| name        | string              | Yes      |
| category    | string              | Yes      |
| quantity    | float               | Yes      |
| unit        | string              | Yes      |
| expire_date | string (yyyy-mm-dd) | Yes      |

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食材 '高麗菜' 已存入冰箱",
  "db_id": 1
}
```

---

### Update Ingredient

修改冰箱中的食材資訊。

**Endpoint**

```
PUT /api/inventory/{item_id}
```

**Path Parameters**

| Field   | Type |
| ------- | ---- |
| item_id | int  |

**Request Body**

| Field       | Type   | Required |
| ----------- | ------ | -------- |
| name        | string | Yes      |
| category    | string | Yes      |
| quantity    | float  | Yes      |
| unit        | string | Yes      |
| expire_date | string | Yes      |

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食材修改成功！名稱已更新為 '高麗菜'"
}
```

**Error Response**

Status Code: `404 Not Found`

```json
{
  "detail": "找不到這筆食材"
}
```

---

### Delete Ingredient

刪除冰箱食材。

**Endpoint**

```
DELETE /api/inventory/{item_id}
```

**Path Parameters**

| Field   | Type |
| ------- | ---- |
| item_id | int  |

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食材 ID 1 已經刪除"
}
```

**Error Response**

Status Code: `404 Not Found`

```json
{
  "detail": "找不到這筆食材"
}
```

---

# Recipe Management

### Get Recipe List

取得所有食譜。

**Endpoint**

```
GET /api/recipes/recommend
```

**Parameters**

N/A

**Response**

Status Code: `200 OK`

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

---

### Add Recipe

新增食譜。

**Endpoint**

```
POST /api/recipes
```

**Request Body**

| Field       | Type   | Required |
| ----------- | ------ | -------- |
| name        | string | Yes      |
| description | string | No       |
| ingredients | array  | Yes      |

Ingredient Object

| Field    | Type   |
| -------- | ------ |
| name     | string |
| category | string |
| quantity | float  |
| unit     | string |

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食譜 '番茄炒蛋' 新增成功！",
  "recipe_id": 1
}
```

---

### Update Recipe

修改食譜。

**Endpoint**

```
PUT /api/recipes/{recipe_id}
```

**Path Parameters**

| Field     | Type |
| --------- | ---- |
| recipe_id | int  |

**Request Body**

| Field       | Type   |
| ----------- | ------ |
| name        | string |
| description | string |
| ingredients | array  |

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食譜 '番茄炒蛋' 修改成功！"
}
```

**Error Response**

Status Code: `404 Not Found`

```json
{
  "detail": "找不到此食譜"
}
```

---

### Delete Recipe

刪除食譜。

**Endpoint**

```
DELETE /api/recipes/{recipe_id}
```

**Response**

Status Code: `200 OK`

```json
{
  "status": "success",
  "message": "食譜已刪除！"
}
```

**Error Response**

Status Code: `404 Not Found`

```json
{
  "detail": "找不到此食譜"
}
```

---

# Smart Recommendation

### Recommend Recipes by Expiring Ingredients

優先推薦能消耗即將過期食材的食譜。

**Endpoint**

```
GET /api/recipes/smart-recommend
```

**Parameters**

N/A

系統自動尋找 3 天內到期的食材，並使用 Greedy (Expiring First) 演算法排序推薦。

**Response**

Status Code: `200 OK`

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
