from decimal import Decimal
from uuid import uuid4
from src.mappers.order_item_mapper import OrderItemMapper
from src.models.product import ProductModel
from src.schemas.order_items import OrderItemCreate


def test_to_models_maps_fields_and_product_price():
    product_id = uuid4()
    product = ProductModel(
        id=product_id,
        name="Widget",
        price=Decimal("12.50"),
        stock=5)
    items = [OrderItemCreate(product_id=product_id, quantity=2)]
    result = OrderItemMapper().to_models(items, {product_id: product})
    assert len(result) == 1
    assert result[0].product_id == product_id
    assert result[0].quantity == 2
    assert result[0].price == Decimal("12.50")