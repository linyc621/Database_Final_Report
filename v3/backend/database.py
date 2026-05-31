import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
from dotenv import load_dotenv

# 讀取 .env 設定
load_dotenv()
# 從環境變數中讀取各自的設定值
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "refrigerator")
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "0000")

# 組合成連線字串
DB_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_db_connection():
    # 保持 RealDictCursor 讓回傳值自動維持字典格式
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# 讀取庫存
def fetch_inventory():
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
    return items

# 新增食材
def insert_fridge_item(name: str, category: str, quantity: float, unit: str, expire_date: date):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 第一步：檢查食材是否存在
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (name,))
        existing_ingredient = cur.fetchone()

        if existing_ingredient:
            target_ingredient_id = existing_ingredient['id']
        else:
            insert_ing_query = """
                INSERT INTO pantry.ingredients (name, category) 
                VALUES (%s, %s) RETURNING id;
            """
            cur.execute(insert_ing_query, (name, category))
            target_ingredient_id = cur.fetchone()['id']

        # 第二步：新增到冰箱
        inventory_query = """
            INSERT INTO pantry.fridge_contents 
            (ingredient_id, quantity, unit, added_date, expire_date) 
            VALUES (%s, %s, %s, CURRENT_DATE, %s) RETURNING id;
        """
        cur.execute(inventory_query, (target_ingredient_id, quantity, unit, expire_date))
        new_record_id = cur.fetchone()['id']
        
        conn.commit()
        return new_record_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
# 修改食材
def update_fridge_item(item_id: int, name: str, category: str, quantity: float, unit: str, expire_date: date):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 第一步：尋找或建立食材基礎資料
        cur.execute("SELECT id FROM pantry.ingredients WHERE name = %s;", (name,))
        existing_ingredient = cur.fetchone()

        if existing_ingredient:
            target_ingredient_id = existing_ingredient['id']
        else:
            insert_ing_query = """
                INSERT INTO pantry.ingredients (name, category) 
                VALUES (%s, %s) RETURNING id;
            """
            cur.execute(insert_ing_query, (name, category))
            target_ingredient_id = cur.fetchone()['id']

        # 第二步：更新冰箱紀錄
        query = """
            UPDATE pantry.fridge_contents 
            SET ingredient_id = %s, quantity = %s, unit = %s, expire_date = %s 
            WHERE id = %s;
        """
        cur.execute(query, (target_ingredient_id, quantity, unit, expire_date, item_id))
        
        # 檢查是否有成功更新到資料
        row_count = cur.rowcount
        conn.commit()
        return row_count > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# 刪除食材
def delete_fridge_item(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "DELETE FROM pantry.fridge_contents WHERE id = %s;"
        cur.execute(query, (item_id,))
        row_count = cur.rowcount
        conn.commit()
        return row_count > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
# 智慧推薦功能 (Algorithm) 
def fetch_smart_recommendation(days_limit: int = 3):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
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
        return results
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

# 基礎食譜清單
def fetch_all_recipes():
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
    return recipes_raw
