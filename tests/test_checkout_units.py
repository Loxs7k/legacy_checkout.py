"""Testes unitários das funções extraídas na refatoração."""

import pytest

from legacy_checkout import (
    calculate_coupon_discount,
    calculate_customer_discount,
    calculate_discount,
    calculate_points,
    calculate_shipping,
    calculate_subtotal,
    calculate_tax,
    calculate_total_weight,
    find_duplicate_products,
)


def test_calculate_subtotal_of_empty_list_is_zero():
    assert calculate_subtotal([]) == 0


def test_calculate_subtotal_ignores_non_positive_quantities():
    items = [
        {"price": 10, "qty": 2},
        {"price": 99, "qty": 0},
        {"price": 99, "qty": -1},
    ]

    assert calculate_subtotal(items) == 20


def test_calculate_total_weight_defaults_missing_weight_to_zero():
    items = [{"qty": 2, "weight": 1.5}, {"qty": 3}]

    assert calculate_total_weight(items) == 3


@pytest.mark.parametrize(
    "customer_type, subtotal, expected",
    [
        ("vip", 999, 99.9),
        ("vip", 1000, 150),
        ("employee", 100, 20),
        ("regular", 799, 0),
        ("regular", 800, 40),
        ("outro", 5000, 0),
    ],
)
def test_calculate_customer_discount(customer_type, subtotal, expected):
    assert calculate_customer_discount(customer_type, subtotal) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    "coupon, customer_type, subtotal, expected",
    [
        ("PROMO10", "regular", 200, 20),
        ("PROMO20", "regular", 500, 100),
        ("PROMO20", "regular", 499, 0),
        ("VIP50", "vip", 100, 50),
        ("VIP50", "regular", 100, 0),
        ("", "vip", 100, 0),
    ],
)
def test_calculate_coupon_discount(coupon, customer_type, subtotal, expected):
    assert calculate_coupon_discount(coupon, customer_type, subtotal) == expected


def test_calculate_discount_is_capped_at_25_percent():
    assert calculate_discount("employee", "PROMO10", 1000) == 250


def test_calculate_shipping_free_only_without_express():
    assert calculate_shipping(500, 10, "MG", express=False) == 0
    assert calculate_shipping(500, 0, "MG", express=True) == 36


def test_calculate_shipping_by_region():
    assert calculate_shipping(100, 10, "SP", express=False) == 24
    assert calculate_shipping(100, 10, "AM", express=False) == 41


@pytest.mark.parametrize(
    "state, expected", [("MG", 7), ("SP", 9), ("RJ", 8), ("ES", 7), ("XX", 12)]
)
def test_calculate_tax_by_state(state, expected):
    assert calculate_tax(100, state) == pytest.approx(expected)


def test_calculate_points_vip_gets_double():
    assert calculate_points("vip", 100) == 20
    assert calculate_points("regular", 100) == 10


def test_find_duplicate_products_of_empty_list_is_empty():
    assert find_duplicate_products([]) == []
