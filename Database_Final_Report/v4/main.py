from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import db

app = FastAPI(title="Smart Pantry API", description="冰箱管家後端 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 資料庫連線設定
from dotenv import load_dotenv
import os
load_dotenv()
DB_URL = os.getenv("DB_URL")

def get_db_connection():
    try:
        return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed",
        )

# 2. 定義資料格式
class FridgeItemCreate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

class FridgeItemUpdate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

class RecipeIngredient(BaseModel):
    name: str
    category: Optional[str] = "未分類"  
    quantity: float
    unit: str

class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    ingredients: List[RecipeIngredient]

class RecipeUpdate(BaseModel):
    name: str
    description: Optional[str] = ""
    ingredients: List[RecipeIngredient]

# 3. API 接口區域

# 冰箱食材(取得、新增、修改、刪除)
@app.get("/api/inventory", summary="取得冰箱所有食材")
def get_inventory():
    return db.get_inventory()

@app.post("/api/inventory", summary="新增食材到冰箱 (自動註冊新食材)")
def add_inventory(item: FridgeItemCreate):
    return db.add_inventory(item)

@app.put("/api/inventory/{item_id}", summary="修改冰箱裡的食材 (包含名稱)")
def update_inventory(item_id: int, item: FridgeItemUpdate):
    return db.update_inventory(item_id, item)

@app.delete("/api/inventory/{item_id}", summary="從冰箱刪除食材")
def delete_inventory(item_id: int):
    return db.delete_inventory(item_id)

# 冰箱食譜(取得、新增、修改、刪除、推薦)
@app.post("/api/recipes", summary="新增食譜")
def create_recipe(recipe: RecipeCreate):
    return db.create_recipe(recipe)

@app.put("/api/recipes/{recipe_id}", summary="修改食譜")
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    return db.update_recipe(recipe_id, recipe)

@app.delete("/api/recipes/{recipe_id}", summary="刪除食譜")
def delete_recipe(recipe_id: int):
    return db.delete_recipe(recipe_id)

@app.get("/api/recipes/smart-recommend", summary="智慧推薦：優先清空即將過期食材")
def get_smart_recommendation():
    return db.get_smart_recommendation()

@app.get("/api/recipes/recommend", summary="取得所有食譜清單")
def get_all_recipes():
    return db.get_all_recipes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
