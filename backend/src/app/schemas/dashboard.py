from pydantic import BaseModel

class DashboardResponse(BaseModel):
    requests: dict
    providers: dict
    caches: dict
    retrieval: dict
    conversation: dict
    summary: dict