"""
Payment module — API routes.

Adjust the two imports below to match your actual project:
  - get_db: your SQLAlchemy session dependency
  - get_current_user: your JWT-auth dependency, returning an object with `.id`
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db          # <-- adjust
from app.core.deps import get_current_user        # <-- adjust

from .schemas import (
    WalletBalanceResponse, WalletTopUpRequest, WalletTopUpResponse,
    CostEstimateRequest, CostEstimateResponse,
    PaymentCreateRequest, PaymentResponse,
    PaymentCaptureRequest, RefundRequest, PaymentHistoryQuery,
)
from .service import (
    PaymentService, InsufficientBalanceError, DuplicatePaymentError,
    PaymentNotFoundError, InvalidPaymentStateError,
)
from .gateway import MockGateway  # swap for AlgorandGateway when ready

router = APIRouter(prefix="/payment", tags=["payment"])
wallet_router = APIRouter(prefix="/wallet", tags=["wallet"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db=db, gateway=MockGateway())


# ---------- Wallet ----------

@wallet_router.get("/balance", response_model=WalletBalanceResponse)
def get_wallet_balance(
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    wallet = service.get_balance(current_user.id)
    return wallet


@wallet_router.post("/add", response_model=WalletTopUpResponse)
def top_up_wallet(
    payload: WalletTopUpRequest,
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    wallet = service.add_funds(current_user.id, payload.amount, payload.external_reference)
    return wallet


# ---------- Cost estimation ----------

@router.get("/estimate", response_model=CostEstimateResponse)
def estimate_cost(
    agent_id: str,
    estimated_tokens: int | None = None,
    service: PaymentService = Depends(get_payment_service),
):
    result = service.estimate_cost(agent_id=agent_id, estimated_tokens=estimated_tokens)
    return result


# ---------- Pay / Capture / Refund ----------

@router.post("/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def pay(
    payload: PaymentCreateRequest,
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    """Authorizes (holds) funds for a task. The execution engine should call
    /payment/capture on success, or the self-healing path should call
    /payment/refund once retries are exhausted."""
    try:
        return service.authorize_payment(
            user_id=current_user.id,
            agent_id=payload.agent_id,
            amount=payload.amount,
            currency=payload.currency,
            idempotency_key=payload.idempotency_key,
            task_id=payload.task_id,
        )
    except InsufficientBalanceError as e:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(e))
    except DuplicatePaymentError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/capture", response_model=PaymentResponse)
def capture(
    payload: PaymentCaptureRequest,
    service: PaymentService = Depends(get_payment_service),
):
    """Called by the Execution Engine once a task completes successfully."""
    try:
        return service.capture_payment(payload.payment_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    except InvalidPaymentStateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/refund", response_model=PaymentResponse)
def refund(
    payload: RefundRequest,
    service: PaymentService = Depends(get_payment_service),
):
    """Called by the Self-Healing module once every agent retry has failed."""
    try:
        return service.refund_payment(payload.payment_id, payload.reason)
    except PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    except InvalidPaymentStateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ---------- History ----------

@router.get("/history", response_model=list[PaymentResponse])
def get_history(
    query: PaymentHistoryQuery = Depends(),
    current_user=Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    return service.get_history(
        user_id=current_user.id,
        status=query.status,
        limit=query.limit,
        offset=query.offset,
    )
