from fastapi import Header, HTTPException

async def get_tenant_id(x_tenant_id: int = Header(...)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant_id header")
    return x_tenant_id