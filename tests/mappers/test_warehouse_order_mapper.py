from decimal import Decimal
from uuid import UUID, uuid4
from src.mappers.warehouse_order_mapper import OrderMapper
from src.models.order import OrderModel, OrderStatus
from src.models.order_item import OrderItemModel


def test_to_model_creates_order_with_items():
    items = [
        OrderItemModel(
            product_id=uuid4(),
            quantity=2,
            price=Decimal("12.50"))]
    result = OrderMapper().to_model(items)
    assert isinstance(result, OrderModel)
    assert isinstance(result.id, UUID)
    assert result.items == items


def test_to_read_maps_order_fields_and_items():
    order_id = uuid4()
    product_id = uuid4()
    order = OrderModel(
        id=order_id,
        status=OrderStatus.PENDING.value,
        items=[
            OrderItemModel(
                product_id=product_id,
                quantity=2,
                price=Decimal("12.50"))])

    result = OrderMapper().to_read(order)
    assert result.id == order_id
    assert result.status == OrderStatus.PENDING.value
    assert result.items[0].product_id == product_id
    assert result.items[0].quantity == 2
    assert result.items[0].price == 12.50