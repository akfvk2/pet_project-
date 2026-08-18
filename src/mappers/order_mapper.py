from uuid import UUID
from src.schemas.orders import OrderResponse, OrderCreateRequest, OrderCreate

class OrderMapper:
    @staticmethod
    def to_create_request(order_in: OrderCreate, user_id: UUID, reference_id: UUID) -> OrderCreateRequest:
        return OrderCreateRequest(
            **order_in.model_dump(),
            user_id=user_id,
            reference_id=reference_id,
        )