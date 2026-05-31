from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
#匯入剛剛在 database.py 寫好的資料庫函數
import database 

app = FastAPI(title="Smart Pantry API", description="冰箱管家後端 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義資料格式 (Pydantic Models)
# 新增食材時需要的格式
class FridgeItemCreate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

# 修改食材時需要的格式
class FridgeItemUpdate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expire_date: date

# 讀取 (Read)
@app.get("/api/inventory", summary="取得冰箱所有食材")
def get_inventory():
    try:
        items = database.fetch_inventory() # 呼叫 database.py 的函數
        return {"status": "success", "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系統錯誤: {e}")

# 新增 (Create)
@app.post("/api/inventory", summary="新增食材到冰箱")
def add_inventory(item: FridgeItemCreate):
    try:
        new_id = database.insert_fridge_item(
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            expire_date=item.expire_date
        )
        return {
            "status": "success", 
            "message": f"食材 '{item.name}' 已存入冰箱", 
            "db_id": new_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系統錯誤: {e}")

# 修改 (Update)
@app.put("/api/inventory/{item_id}", summary="修改冰箱裡的食材")
def update_inventory(item_id: int, item: FridgeItemUpdate):
    try:
        success = database.update_fridge_item(
            item_id=item_id,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            expire_date=item.expire_date
        )
        if not success:
            raise HTTPException(status_code=404, detail="找不到這筆食材紀錄")
        
        return {"status": "success", "message": f"食材修改成功！名稱已更新為 '{item.name}'"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失敗: {e}")

# 刪除 (Delete)
@app.delete("/api/inventory/{item_id}", summary="從冰箱刪除食材")
def delete_inventory(item_id: int):
    try:
        success = database.delete_fridge_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="找不到這筆食材紀錄")
        
        return {"status": "success", "message": f"食材 ID {item_id} 已經刪除"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除失敗: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)