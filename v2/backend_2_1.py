from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Pantry API", description="冰箱管家後端 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_methods=["*"],  # 允許所有方法 (GET, POST, PUT, DELETE)
    allow_headers=["*"],
)

# 1. 資料庫連線設定
# 記得修改成你自己的資料庫連線資訊、以及隱藏密碼
DB_URL = "postgresql://postgres:0000@localhost:5432/project"

def get_db_connection():
    try:
        # 使用RealDictCursor讓回傳的資料自動變成JSON格式
        return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed",
        )

# 2.定義資料格式
# 新增食材時需要的資料
class FridgeItemCreate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

# 修改食材時需要的資料
class FridgeItemUpdate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

# 3. API 接口區域 (CRUD + 演算法)
# 讀取 (Read)
@app.get("/api/inventory", summary="取得冰箱所有食材")
def get_inventory():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            fridge_contents.id, 
            ingredients.name, 
            ingredients.category,
            fridge_contents.quantity, 
            fridge_contents.unit, 
            fridge_contents.expire_date 
        FROM pantry.fridge_contents
        JOIN pantry.ingredients ON fridge_contents.ingredient_id = ingredients.id
        ORDER BY fridge_contents.expire_date ASC;
    """
    cur.execute(query)
    items = cur.fetchall()
    cur.close()
    conn.close()
    return {"status": "success", "data": items}

# 新增 (Create)
@app.post("/api/inventory", summary="新增食材到冰箱 (自動註冊新食材)")
def add_inventory(item: FridgeItemCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 第一步：檢查食材名稱是否已存在於基礎清單
        # 使用name來搜尋是否存在
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (item.name,))
        existing_ingredient = cur.fetchone()

        if existing_ingredient:
            # 如果食材已存在，取得它的ID
            target_ingredient_id = existing_ingredient['id']
        else:
            # 如果是新食材，先在基礎清單 (ingredients) 建立一筆新資料
            # 這裡會根據你前端傳來的 category 自動分類
            insert_ing_query = """
                INSERT INTO pantry.ingredients (name, category) 
                VALUES (%s, %s) RETURNING id;
            """
            cur.execute(insert_ing_query, (item.name, item.category))
            target_ingredient_id = cur.fetchone()['id']

        # 第二步：執行新增到冰箱 (fridge_contents) 
        # 每一筆新增都會有獨立的 id，所以不同到期日的同名食材會分開存儲
        inventory_query = """
            INSERT INTO pantry.fridge_contents 
            (ingredient_id, quantity, unit, added_date, expire_date) 
            VALUES (%s, %s, %s, CURRENT_DATE, %s) RETURNING id;
        """
        cur.execute(inventory_query, (
            target_ingredient_id, 
            item.quantity, 
            item.unit, 
            item.expire_date
        ))
        new_record_id = cur.fetchone()['id']
        
        # 存檔 Commit
        conn.commit()
        return {
            "status": "success", 
            "message": f"食材 '{item.name}' 已存入冰箱", 
            "db_id": new_record_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"系統錯誤: {e}")
    finally:
        cur.close()
        conn.close()

# 修改 (Update) 
@app.put("/api/inventory/{item_id}", summary="修改冰箱裡的食材 (包含名稱)")
def update_inventory(item_id: int, item: FridgeItemUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 第一步：處理食材名稱 (跟新增的邏輯一樣，尋找或建立新食材)
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (item.name,))
        existing_ingredient = cur.fetchone()

        if existing_ingredient:
            target_ingredient_id = existing_ingredient['id']
        else:
            insert_ing_query = """
                INSERT INTO pantry.ingredients (name, category) 
                VALUES (%s, %s) RETURNING id;
            """
            cur.execute(insert_ing_query, (item.name, item.category))
            target_ingredient_id = cur.fetchone()['id']

        # 第二步：更新冰箱紀錄 (fridge_contents) 的所有欄位，包含 ingredient_id
        query = """
            UPDATE pantry.fridge_contents 
            SET ingredient_id = %s, quantity = %s, unit = %s, expire_date = %s 
            WHERE id = %s;
        """
        cur.execute(query, (target_ingredient_id, item.quantity, item.unit, item.expire_date, item_id))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="找不到這筆食材")
        
        conn.commit()
        return {"status": "success", "message": f"食材修改成功！名稱已更新為 '{item.name}'"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"修改失敗: {e}")
    finally:
        cur.close()
        conn.close()

# 刪除 (Delete) 
@app.delete("/api/inventory/{item_id}", summary="從冰箱刪除食材")
def delete_inventory(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "DELETE FROM pantry.fridge_contents WHERE id = %s;"
        cur.execute(query, (item_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="找不到這筆食材")
        conn.commit()
        return {"status": "success", "message": f"食材 ID {item_id} 已經刪除"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"刪除失敗: {e}")
    finally:
        cur.close()
        conn.close()

# 智慧推薦 (Greedy Algorithm) 
@app.get("/api/recipes/smart-recommend", summary="智慧推薦：優先清空即將過期食材")
def get_smart_recommendation():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 貪婪演算法：找出包含最多「3天內過期食材」的食譜
        days_limit = 3
        query = """
            WITH expiring_items AS (
                SELECT DISTINCT ingredient_id
                FROM pantry.fridge_contents
                WHERE expire_date <= CURRENT_DATE + CAST(%s AS INTERVAL)
            )
            SELECT 
                r.name AS recipe_name,
                r.description,
                COUNT(ri.ingredient_id) AS emergency_count
            FROM pantry.recipes r
            JOIN pantry.recipe_ingredients ri ON r.id = ri.recipe_id
            JOIN expiring_items ei ON ri.ingredient_id = ei.ingredient_id
            GROUP BY r.id, r.name, r.description
            ORDER BY emergency_count DESC;
        """
        cur.execute(query, (f"{days_limit} days",))
        results = cur.fetchall()
        return {"status": "success", "algorithm": "Greedy (Expiring First)", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推薦失敗: {e}")
    finally:
        cur.close()
        conn.close()

# 原有的基本食譜查詢
@app.get("/api/recipes/recommend", summary="取得所有食譜清單")
def get_all_recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT recipes.name AS recipe_name, ingredients.name AS ingredient_name, 
               recipe_ingredients.quantity, recipe_ingredients.unit
        FROM pantry.recipe_ingredients
        JOIN pantry.recipes ON recipe_ingredients.recipe_id = recipes.id
        JOIN pantry.ingredients ON recipe_ingredients.ingredient_id = ingredients.id;
    """
    cur.execute(query)
    recipes_raw = cur.fetchall()
    cur.close()
    conn.close()
    
    structured = {}
    for row in recipes_raw:
        r_name = row['recipe_name']
        if r_name not in structured:
            structured[r_name] = {"name": r_name, "ingredients": []}
        structured[r_name]["ingredients"].append({
            "item": row['ingredient_name'], "qty": row['quantity'], "unit": row['unit']
        })
    return {"status": "success", "data": list(structured.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
