"""
/api/v1/history - Recent analysis history
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from utils.storage import ResultStorage

router = APIRouter()


@router.get("/history")
async def get_history(limit: int = Query(default=20, le=100)):
    """Return the N most recent analysis results (stored in memory/JSON)."""
    results = ResultStorage.get_recent(limit)
    return {"results": results, "total": len(results)}


@router.get("/history/{result_id}")
async def get_result(result_id: str):
    """Fetch a specific result by ID."""
    result = ResultStorage.get_by_id(result_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.delete("/history")
async def clear_history():
    """Clear all stored results."""
    ResultStorage.clear()
    return {"message": "History cleared"}
