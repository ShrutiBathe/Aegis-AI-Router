from fastapi import FastAPI

from app.payments.router import router as payment_router
from app.execution.router import router as execution_router
from app.self_healing.router import router as healing_router
from app.reputation.router import router as reputation_router


app = FastAPI(title="B2 Module Testing")

app.include_router(payment_router)
app.include_router(execution_router)
app.include_router(healing_router)
app.include_router(reputation_router)
