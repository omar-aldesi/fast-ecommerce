import asyncio
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.core import logger
from app.models import User, Order, OrderItem, Branch, Product, VariationOption, ProductVariation, Addon, \
    ShippingAddress, ShippingOrder, Payment
from app.schemas.order import OrderCreate
from app.core.utils import check_product_stocks, get_or_create
from decimal import Decimal
from datetime import datetime
from app.crud.notification import create_notification
from app.schemas.payment import PaymentRequestSchema


def check_branch_exists(db: Session, branch_id: int):
    if not db.query(Branch).filter(and_(Branch.id == branch_id)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")


def create_new_order(order: OrderCreate, user: User) -> Order:
    return Order(
        user_id=user.id,
        type=order.type.value,
        branch_id=order.branch_id,
    )


def process_addons(db: Session, db_product: Product, order_product,
                   new_order_item: OrderItem) -> Decimal:
    total_addon_price = Decimal('0.00')
    for addon in order_product.addons:
        db_addon = db.query(Addon).get(addon.id)
        if not db_addon:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Addon {addon.id} not found")
        if db_addon not in db_product.addons:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid addon")
        total_addon_price += Decimal(str(db_addon.price)) + Decimal(str(db_addon.tax))
        new_order_item.addons.append(db_addon)
    return total_addon_price


def process_variations(db: Session, db_product: Product, order_product, new_order_item: OrderItem):
    variations = set()
    total_variation_price = Decimal('0.00')
    for variation in order_product.variations:
        product_variation: ProductVariation = db.query(ProductVariation).get(variation.id)
        if not product_variation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variation {variation.id} not found")
        if product_variation not in db_product.variations:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid variation")
        variations.add(product_variation)
        new_order_item.variations.append(product_variation)
        if len(variation.options) < product_variation.min_selections or len(
                variation.options) > product_variation.max_selections:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid variation options number")
        for option in variation.options:
            variation_option = db.query(VariationOption).get(option.id)
            if not variation_option:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Variation option {option.id} not found")
            total_variation_price += Decimal(str(variation_option.price))
    return total_variation_price, variations


def check_required_variations(db_product: Product, variations: set):
    for db_product_variation in db_product.variations:
        if db_product_variation.required and db_product_variation not in variations:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Variation {db_product_variation.title} is required")


def process_order_product(db: Session, order: OrderCreate, order_product,
                          new_order: Order) -> Decimal:
    db_product: Optional[Product] = db.query(Product).filter(
        and_(Product.id == order_product.product_id),
        and_(Product.branch_id == order.branch_id)
    ).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {order_product.product_id} not found")
    if not check_product_stocks(db, db_product, order_product.quantity):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stocks")

    new_order_item = OrderItem(
        quantity=order_product.quantity,
        product_id=order_product.product_id,
    )

    total_order_item_price = Decimal(str(db_product.price)) * Decimal(str(order_product.quantity))
    total_order_item_price += process_addons(db, db_product, order_product, new_order_item)
    variation_price, variations = process_variations(db, db_product, order_product, new_order_item)
    total_order_item_price += variation_price

    check_required_variations(db_product, variations)

    new_order_item.total_price = total_order_item_price
    new_order.items.append(new_order_item)

    return total_order_item_price


def create_or_get_shipping_address(db: Session, shipping_address_data: dict) -> ShippingAddress:
    shipping_address, _ = get_or_create(db, ShippingAddress, **shipping_address_data)
    return shipping_address


def validate_and_set_schedule(order: OrderCreate, new_order: Order):
    if order.is_scheduled:
        if order.scheduled_at is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheduled at is required")
        if order.scheduled_at < datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheduled at")
        new_order.scheduled_at = order.scheduled_at
        new_order.is_scheduled = True


def create_shipping_order(db: Session, total_price: Decimal, order_id: int, user_id: int):
    # for testing purposes
    shipping_order = ShippingOrder(
        fee=total_price * Decimal(str(0.01)),
        status="pending",
        order_id=order_id,
        shipping_client="test",
        shipping_client_data={},
        user_id=user_id
    )
    db.add(shipping_order)


def create_payment(db: Session, amount: Decimal, order_id: int, user_id: int, payment_data: PaymentRequestSchema):
    print(order_id)
    payment = Payment(
        amount=amount,
        status="accepted",
        order_id=order_id,
        user_id=user_id,
        **payment_data.model_dump()
    )
    db.add(payment)


async def create_order(db: Session, order: OrderCreate, user: User) -> Order:
    logger.info("Creating new order for user : #{user.id}")
    check_branch_exists(db, order.branch_id)
    new_order = create_new_order(order, user)
    total_order_price = Decimal('0.00')

    if len(order.products) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No products in order")

    shipping_address = create_or_get_shipping_address(db, order.shipping_address.model_dump())
    new_order.shipping_address_id = shipping_address.id

    validate_and_set_schedule(order, new_order)

    for order_product in order.products:
        total_order_price += process_order_product(db, order, order_product, new_order)
    new_order.total_price = total_order_price
    db.add(new_order)
    db.flush()
    create_shipping_order(db, total_order_price, new_order.id, user.id)
    create_payment(db, total_order_price, new_order.id, user.id, order.payment)
    logger.info(f"Order {new_order.id} created")
    db.commit()
    await asyncio.create_task(create_notification(user.id, f"New order {new_order.id} created"))
    return new_order
