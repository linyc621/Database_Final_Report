from functools import wraps
from fastapi import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from models import (
    FridgeItemCreate,
    FridgeItemUpdate,
    RecipeCreate,
    RecipeUpdate,
)

load_dotenv()

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")

def with_db_cursor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            result = func(cur, *args, **kwargs)
            conn.commit()
            return result
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=400, detail=f"資料庫操作失敗: {e}")
        finally:
            cur.close()
            conn.close()
    return wrapper

@with_db_cursor
def get_inventory(cur):
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
    return {"status": "success", "data": items}

@with_db_cursor
def add_inventory(cur, item: FridgeItemCreate):
    cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (item.name,))
    existing_ingredient = cur.fetchone()
    
    if existing_ingredient:
        target_ingredient_id = existing_ingredient['id']
    else:
        insert_ing_query = "INSERT INTO pantry.ingredients (name, category) VALUES (%s, %s) RETURNING id;"
        cur.execute(insert_ing_query, (item.name, item.category))
        target_ingredient_id = cur.fetchone()['id']

    inventory_query = """
        INSERT INTO pantry.fridge_contents 
        (ingredient_id, quantity, unit, added_date, expire_date) 
        VALUES (%s, %s, %s, CURRENT_DATE, %s) RETURNING id;
    """
    cur.execute(inventory_query, (target_ingredient_id, item.quantity, item.unit, item.expire_date))
    new_record_id = cur.fetchone()['id']
    
    return {
        "status": "success",
        "message": f"食材 '{item.name}' 已存入冰箱",
        "db_id": new_record_id,
    }
        
@with_db_cursor
def update_inventory(cur, item_id: int, item: FridgeItemUpdate): 
    cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (item.name,))
    existing_ingredient = cur.fetchone()

    if existing_ingredient:
        target_ingredient_id = existing_ingredient['id']
    else:
        insert_ing_query = "INSERT INTO pantry.ingredients (name, category) VALUES (%s, %s) RETURNING id;"
        cur.execute(insert_ing_query, (item.name, item.category))
        target_ingredient_id = cur.fetchone()['id']

    query = """
        UPDATE pantry.fridge_contents 
        SET ingredient_id = %s, quantity = %s, unit = %s, expire_date = %s 
        WHERE id = %s;
    """
    cur.execute(query, (target_ingredient_id, item.quantity, item.unit, item.expire_date, item_id))
    
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="找不到這筆食材")
    
    return {
        "status": "success",
        "message": f"食材修改成功！名稱已更新為 '{item.name}'",
    }
        
@with_db_cursor
def delete_inventory(cur, item_id: int):
    query = "DELETE FROM pantry.fridge_contents WHERE id = %s;"
    cur.execute(query, (item_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="找不到這筆食材")
    return {"status": "success", "message": f"食材 ID {item_id} 已經刪除"}
        
@with_db_cursor
def get_all_recipes(cur):
    query = """
        SELECT recipes.id AS recipe_id, recipes.name AS recipe_name, recipes.description,
               ingredients.name AS ingredient_name, 
               recipe_ingredients.quantity, recipe_ingredients.unit
        FROM pantry.recipes
        LEFT JOIN pantry.recipe_ingredients ON recipes.id = recipe_ingredients.recipe_id
        LEFT JOIN pantry.ingredients ON recipe_ingredients.ingredient_id = ingredients.id;
    """
    cur.execute(query)
    recipes_raw = cur.fetchall()
    
    structured = {}
    for row in recipes_raw:
        r_id = row['recipe_id']
        if r_id not in structured:
            structured[r_id] = {
                "id": r_id, 
                "name": row['recipe_name'], 
                "description": row['description'],
                "ingredients": []
            }
        if row['ingredient_name']:
            structured[r_id]["ingredients"].append({
                "item": row['ingredient_name'], 
                "qty": row['quantity'], 
                "unit": row['unit']
            })
    return {"status": "success", "data": list(structured.values())}

@with_db_cursor
def create_recipe(cur, recipe: RecipeCreate):
    cur.execute(
        "INSERT INTO pantry.recipes (name, description) VALUES (%s, %s) RETURNING id;", 
        (recipe.name, recipe.description)
    )
    recipe_id = cur.fetchone()['id']

    for ing in recipe.ingredients:
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (ing.name,))
        exist_ing = cur.fetchone()
        
        if exist_ing:
            ing_id = exist_ing['id']
        else:
            cur.execute(
                "INSERT INTO pantry.ingredients (name, category) VALUES (%s, %s) RETURNING id;",
                (ing.name, ing.category)
            )
            ing_id = cur.fetchone()['id']
        
        cur.execute(
            "INSERT INTO pantry.recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (%s, %s, %s, %s);",
            (recipe_id, ing_id, ing.quantity, ing.unit)
        )
            
    return {
        "status": "success",
        "message": f"食譜 '{recipe.name}' 新增成功！",
        "recipe_id": recipe_id,
    }
        
@with_db_cursor
def update_recipe(cur, recipe_id: int, recipe: RecipeUpdate):
    cur.execute(
        "UPDATE pantry.recipes SET name = %s, description = %s WHERE id = %s;",
        (recipe.name, recipe.description, recipe_id)
    )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="找不到此食譜")

    cur.execute("DELETE FROM pantry.recipe_ingredients WHERE recipe_id = %s;", (recipe_id,))

    for ing in recipe.ingredients:
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (ing.name,))
        exist_ing = cur.fetchone()
        
        if exist_ing:
            ing_id = exist_ing['id']
        else:
            cur.execute(
                "INSERT INTO pantry.ingredients (name, category) VALUES (%s, %s) RETURNING id;",
                (ing.name, ing.category)
            )
            ing_id = cur.fetchone()['id']
            
        cur.execute(
            "INSERT INTO pantry.recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (%s, %s, %s, %s);",
            (recipe_id, ing_id, ing.quantity, ing.unit)
        )
            
    return {
        "status": "success",
        "message": f"食譜 '{recipe.name}' 修改成功！",
    }

@with_db_cursor
def delete_recipe(cur, recipe_id: int):
    cur.execute("DELETE FROM pantry.recipe_ingredients WHERE recipe_id = %s;", (recipe_id,))
    cur.execute("DELETE FROM pantry.recipes WHERE id = %s;", (recipe_id,))
    
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="找不到此食譜")
        
    return {"status": "success", "message": f"食譜已刪除！"}
        
@with_db_cursor
def get_smart_recommendation(cur):
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