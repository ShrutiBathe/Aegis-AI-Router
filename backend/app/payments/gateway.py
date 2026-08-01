"""
Payment gateway abstraction.

Keeping this separate from PaymentService means your service logic
(authorize/capture/refund, wallet math, idempotency) never has to change
when you swap the mock gateway out for the real Algorand SDK + x402 client.
Build and demo against MockGateway now; wire in AlgorandGateway once the
blockchain side is ready, with zero changes to service.py or router.py.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
import uuid


@dataclass
class GatewayResult:
    success: bool
    transaction_id: str
    error: str | None = None


class PaymentGateway(ABC):
    @abstractmethod
    def authorize(self, amount: Decimal, currency: str, reference: str) -> GatewayResult:
        """Hold funds. Does not move money yet."""

    @abstractmethod
    def capture(self, transaction_id: str) -> GatewayResult:
        """Actually settle a previously authorized hold."""

    @abstractmethod
    def refund(self, transaction_id: str, amount: Decimal) -> GatewayResult:
        """Return funds for an authorized or captured transaction."""


class MockGateway(PaymentGateway):
    """In-memory gateway for local dev / demo. Always succeeds.
    Swap for AlgorandGateway (x402 protocol) when ready."""

    def authorize(self, amount: Decimal, currency: str, reference: str) -> GatewayResult:
        return GatewayResult(success=True, transaction_id=f"mock_auth_{uuid.uuid4().hex[:12]}")

    def capture(self, transaction_id: str) -> GatewayResult:
        return GatewayResult(success=True, transaction_id=transaction_id)

    def refund(self, transaction_id: str, amount: Decimal) -> GatewayResult:
        return GatewayResult(success=True, transaction_id=f"mock_refund_{uuid.uuid4().hex[:12]}")


class AlgorandGateway(PaymentGateway):
    """
    Real implementation stub — wire up the Algorand SDK + x402 client here.

    x402 is a request-response protocol layered on HTTP 402; a typical flow is:
      1. authorize(): send a signed x402 payment request, get back a payment_id
         once the payer's wallet confirms the hold.
      2. capture(): submit the actual Algorand transaction to settle.
      3. refund(): submit a reverse transaction referencing the original tx id.

    Leaving this unimplemented on purpose — plug in `algosdk` + your x402
    client here without touching PaymentService.
    """

    def __init__(self, algod_client=None, x402_client=None):
        self.algod_client = algod_client
        self.x402_client = x402_client

    def authorize(self, amount: Decimal, currency: str, reference: str) -> GatewayResult:
        raise NotImplementedError("Wire up algosdk + x402 client here")

    def capture(self, transaction_id: str) -> GatewayResult:
        raise NotImplementedError("Wire up algosdk + x402 client here")

    def refund(self, transaction_id: str, amount: Decimal) -> GatewayResult:
        raise NotImplementedError("Wire up algosdk + x402 client here")
