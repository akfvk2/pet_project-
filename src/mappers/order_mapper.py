from uuid import UUID
from src.schemas.orders import OrderResponse, OrderCreateRequest, OrderCreate

class OrderMapper:
    @staticmethod
    def to_order(data: dict) -> OrderResponse:
        return OrderResponse.model_validate(data)

    @staticmethod
    def to_orders(data: list[dict]) -> list[OrderResponse]:
        return [OrderResponse.model_validate(item) for item in data]

    @staticmethod
    def to_create_request(order_in: OrderCreate, user_id: UUID, reference_id: UUID) -> OrderCreateRequest:
        return OrderCreateRequest(
            **order_in.model_dump(),
            user_id=user_id,
            reference_id=reference_id,
        )

    @staticmethod
    def to_orders_by_user_params(user_id: UUID) -> dict:
        return {"user_id": str(user_id)}