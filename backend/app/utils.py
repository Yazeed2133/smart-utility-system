from fastapi import HTTPException


def get_object_or_404(obj, message: str):
    if not obj:
        raise HTTPException(status_code=404, detail=message)
    return obj