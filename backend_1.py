from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date

app = FastAPI(title="Smart Pantry API", description="冰箱管家後端 API")

# 1. 資料庫連線設定 (請替換成你的 Supabase 連線字串)
DB_URL = "postgresql://postgres:0000@localhost:5432/project"

def get_db_connection():
    try:
        # 使用 RealDictCursor 可以讓回傳的資料自動變成 JSON 格式 (字典)
        return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# 2. 定義前端傳來的資料格式 (Pydantic Models)
class NewIngredient(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

# ==========================================
# API 接口區域
# ==========================================

@app.get("/api/inventory", summary="取得冰箱所有食材")
def get_inventory():
    """
    前端呼叫這個 API，後端就會執行你的測試 SQL 並回傳 JSON。
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 這裡直接使用你寫好的 JOIN 查詢，我多加了 category 讓前端可以分類層架
    query = """
        SELECT 
            fridge_contents.id, 
            ingredients.name, 
            ingredients.category,
            fridge_contents.quantity, 
            fridge_contents.unit, 
            fridge_contents.expire_date 
        FROM pantry.fridge_contents
        JOIN pantry.ingredients 
        ON fridge_contents.ingredient_id = ingredients.id
        ORDER BY fridge_contents.expire_date ASC;
    """
    
    cur.execute(query)
    items = cur.fetchall()
    
    cur.close()
    conn.close()
    return {"status": "success", "data": items}

@app.get("/api/recipes/recommend", summary="取得推薦食譜")
def get_recommended_recipes():
    """
    這是一個簡單的邏輯範例：直接回傳資料庫裡的所有食譜清單與材料
    （未來你可以在這裡加入 AI 判斷快過期食材的邏輯）
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 使用你寫好的食譜測試查詢
    query = """
        SELECT 
            recipes.name AS recipe_name, 
            ingredients.name AS ingredient_name, 
            recipe_ingredients.quantity, 
            recipe_ingredients.unit
        FROM pantry.recipe_ingredients
        JOIN pantry.recipes ON recipe_ingredients.recipe_id = recipes.id
        JOIN pantry.ingredients ON recipe_ingredients.ingredient_id = ingredients.id;
    """
    cur.execute(query)
    recipes_raw = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # 將平坦的 SQL 結果整理成結構化的 JSON
    structured_recipes = {}
    for row in recipes_raw:
        r_name = row['recipe_name']
        if r_name not in structured_recipes:
            structured_recipes[r_name] = {"name": r_name, "ingredients": []}
        
        structured_recipes[r_name]["ingredients"].append({
            "item": row['ingredient_name'],
            "qty": row['quantity'],
            "unit": row['unit']
        })

    return {"status": "success", "data": list(structured_recipes.values())}

# 如果直接執行此檔案，啟動伺服器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)