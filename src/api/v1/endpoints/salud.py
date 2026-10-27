from fastapi import APIRouter

router = APIRouter()


@router.get("/salud", include_in_schema=False)
def salud():
    return {"ok": True}
