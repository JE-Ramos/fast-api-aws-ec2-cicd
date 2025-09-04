from typing import Any, Dict

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/items")
async def get_items() -> Dict[str, Any]:
    return {
        "items": [
            {"id": 1, "name": "Item 1", "version": "1.0"},
            {"id": 2, "name": "Item 2", "version": "1.0"},
            {"id": 3, "name": "Test Item", "version": "1.0"},
        ],
        "api_version": "v1",
        "total": 3,
    }


@router.get("/items/{item_id}")
async def get_item(item_id: int) -> Dict[str, Any]:
    if item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "name": f"Item {item_id}", "version": "1.0", "api_version": "v1"}


@router.post("/items")
async def create_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {"message": "Item created", "item": item}
