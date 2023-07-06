import pytest

from ..channel.utils import create_channel
from ..product.utils import (
    create_category,
    create_product,
    create_product_channel_listing,
    create_product_type,
    create_product_variant,
    create_product_variant_channel_listing,
)
from ..shipping_zone.utils import create_shipping_zone
from ..utils import assign_permissions
from ..warehouse.utils import create_warehouse, update_warehouse
from .utils import checkout_create, raw_checkout_dummy_payment_create


def prepare_product(
    e2e_staff_api_client,
    permission_manage_products,
    permission_manage_channels,
    permission_manage_product_types_and_attributes,
    permission_manage_shipping,
):
    permissions = [
        permission_manage_products,
        permission_manage_channels,
        permission_manage_product_types_and_attributes,
        permission_manage_shipping,
    ]

    assign_permissions(e2e_staff_api_client, permissions)
    warehouse_data = create_warehouse(e2e_staff_api_client)
    warehouse_id = warehouse_data["id"]
    warehouse_ids = [warehouse_id]

    update_warehouse(
        e2e_staff_api_client,
        warehouse_data["id"],
    )

    channel_data = create_channel(
        e2e_staff_api_client, slug="test___0e00", warehouse_ids=warehouse_ids
    )
    channel_id = channel_data["id"]
    channel_ids = [channel_id]
    channel_slug = channel_data["slug"]

    shipping_zone_data = create_shipping_zone(
        e2e_staff_api_client,
        warehouse_ids=warehouse_ids,
        channel_ids=channel_ids,
    )
    shipping_zone_id = shipping_zone_data["id"]

    product_type_data = create_product_type(
        e2e_staff_api_client,
        is_shipping_required=True,
    )
    product_type_id = product_type_data["id"]

    category_data = create_category(
        e2e_staff_api_client,
    )
    category_id = category_data["id"]

    product_data = create_product(
        e2e_staff_api_client,
        product_type_id,
        category_id,
    )
    product_id = product_data["id"]

    create_product_channel_listing(e2e_staff_api_client, product_id, channel_id)

    stocks = [
        {
            "warehouse": warehouse_data["id"],
            "quantity": 5,
        }
    ]
    variant_data = create_product_variant(
        e2e_staff_api_client, product_id, stocks=stocks
    )
    variant_id = variant_data["id"]

    create_product_variant_channel_listing(
        e2e_staff_api_client,
        variant_id,
        channel_id,
    )

    return variant_id, channel_slug, warehouse_id, shipping_zone_id


@pytest.mark.e2e
def test_unlogged_customer_should_not_be_able_to_buy_product_without_shipping_option(
    e2e_not_logged_api_client,
    e2e_staff_api_client,
    permission_manage_products,
    permission_manage_channels,
    permission_manage_product_types_and_attributes,
    permission_manage_shipping,
):
    # Before
    variant_id, channel_slug, shipping_zone_id, warehouse_id = prepare_product(
        e2e_staff_api_client,
        permission_manage_products,
        permission_manage_channels,
        permission_manage_product_types_and_attributes,
        permission_manage_shipping,
    )

    # Step 1 - Create checkout with no shipping method
    lines = [
        {"variantId": variant_id, "quantity": 1},
    ]
    checkout_data = checkout_create(
        e2e_not_logged_api_client,
        lines,
        channel_slug,
        email="jon.doe@saleor.io",
        set_default_billing_address=True,
        set_default_shipping_address=True,
    )
    checkout_id = checkout_data["id"]
    checkout_shipping_required = checkout_data["isShippingRequired"]
    shipping_methods = checkout_data["shippingMethods"]

    total_gross_amount = checkout_data["totalPrice"]["gross"]["amount"]
    assert checkout_shipping_required is True
    assert shipping_methods == []
    assert checkout_data["availableCollectionPoints"] == []

    # Step 2 - Create dummy payment and verify no purchase was made
    checkout_payment_data = raw_checkout_dummy_payment_create(
        e2e_not_logged_api_client, checkout_id, total_gross_amount
    )
    errors = checkout_payment_data["errors"]

    assert errors[0]["code"] == "SHIPPING_METHOD_NOT_SET"
    assert errors[0]["field"] == "shippingMethod"
    assert errors[0]["message"] == "Shipping method is not set"
