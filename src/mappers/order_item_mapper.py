from uuid import UUID
from src.models.order_item import OrderItemModel
from src.models.product import ProductModel
from src.schemas.order_items import OrderItemCreate


class OrderItemMapper:
    def to_models(self, items: list[OrderItemCreate], products_by_id: dict[UUID, ProductModel]) -> list[OrderItemModel]:
        return [
            OrderItemModel(
                product_id=item.product_id,
                quantity=item.quantity,
                price=products_by_id[item.product_id].price,
            )
            for item in items]