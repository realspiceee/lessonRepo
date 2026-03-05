from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os

router = APIRouter(prefix="/products", tags=["medicines"])

class Medicine(BaseModel):
    id: int
    name: str         
    manufacturer: str   
    price: float      
    expiry_date: str    
    in_stock: bool      

data_file = "data.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

medicines_data = load_data()

@router.get("/", response_model=List[Medicine])
def get_medicines(sorting: Optional[str] = Query(None), manufacturer: Optional[str] = Query(None)):
    result = medicines_data.copy()
    
    if sorting == "asc":
        result = sorted(result, key=lambda x: x["name"])
    elif sorting == "desc":
        result = sorted(result, key=lambda x: x["name"], reverse=True)
    
    if manufacturer:
        result = [m for m in result if manufacturer.lower() in m["manufacturer"].lower()]
    
    return result


@router.post("/", response_model=Medicine)
def create_medicine(medicine: Medicine):
    if any(m["id"] == medicine.id for m in medicines_data):
        raise HTTPException(400, "ID существует")
    medicines_data.append(medicine.dict())
    save_data(medicines_data)
    return medicine

@router.put("/{medicine_id}", response_model=Medicine)
def update_medicine(medicine_id: int, medicine: Medicine):
    for i, m in enumerate(medicines_data):
        if m["id"] == medicine_id:
            medicines_data[i] = medicine.dict()
            save_data(medicines_data)
            return medicine
    raise HTTPException(404, "Не найдено")

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int):
    global medicines_data
    medicines_data = [m for m in medicines_data if m["id"] != medicine_id]
    save_data(medicines_data)
    return {"message": "Удалено"}
