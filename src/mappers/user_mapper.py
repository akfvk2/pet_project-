from src.schemas.users import UserRead, UserWithOrdersRead, OrderConfirmationStatus
from src.schemas.orders import OrderResponse


class UserMapper:
    @staticmethod
    def to_user_with_orders(
        user_data: UserRead,
        orders: list[OrderResponse],
        order_status: OrderConfirmationStatus = OrderConfirmationStatus.CONFIRMED,
    ) -> UserWithOrdersRead:
        return UserWithOrdersRead(
            **user_data.model_dump(),
            orders=orders,
            order_status=order_status,
        )