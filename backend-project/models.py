from pydantic import BaseModel
from typing import List, Optional
from datetime import date

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