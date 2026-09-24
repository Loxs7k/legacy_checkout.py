# test_legacy_checkout.py

from legacy_checkout import process_order


def test_regular_customer():
    customer = {
        "name": "Ana",
        "type": "regular"
    }

    items = [
        {
            "name": "Notebook",
            "price": 1000.00,
            "qty": 1,
            "weight": 2
        }
    ]

    result = process_order(
        customer,
        items,
        state="MG"
    )

    assert result["subtotal"] == 1000.00
    assert result["discount"] == 50.00
    assert result["shipping"] == 0
    assert result["tax"] == 66.50
    assert result["total"] == 1016.50


def test_vip_customer():
    customer = {
        "name": "Carlos",
        "type": "vip"
    }

    items = [
        {
            "name": "Monitor",
            "price": 600,
            "qty": 2,
            "weight": 3
        }
    ]

    result = process_order(
        customer,
        items,
        state="SP"
    )

    assert result["subtotal"] == 1200
    assert result["discount"] == 180


def test_coupon():
    customer = {
        "name": "Maria",
        "type": "regular"
    }

    items = [
        {
            "name": "Teclado",
            "price": 200,
            "qty": 2,
            "weight": 1
        }
    ]

    result = process_order(
        customer,
        items,
        coupon="PROMO10",
        state="MG"
    )

    assert result["discount"] == 40


def test_duplicate_products():
    customer = {
        "name": "João",
        "type": "regular"
    }

    items = [
        {"name": "Mouse", "price": 100, "qty": 1, "weight": 0.2},
        {"name": "Mouse", "price": 100, "qty": 1, "weight": 0.2},
        {"name": "Teclado", "price": 200, "qty": 1, "weight": 1}
    ]

    result = process_order(customer, items)

    assert result["duplicate_products"] == ["Mouse"]


# ---------------------------------------------------------------------------
# Testes de caracterização adicionados pela equipe.
# Eles documentam o comportamento do sistema legado e protegem a refatoração.
# ---------------------------------------------------------------------------

import pytest

import legacy_checkout


def make_customer(customer_type="regular", name="Cliente"):
    return {"name": name, "type": customer_type}


def make_item(price, qty=1, weight=0, name="Produto"):
    return {"name": name, "price": price, "qty": qty, "weight": weight}


def order(customer_type="regular", items=None, **kwargs):
    items = items if items is not None else [make_item(100)]
    return process_order(make_customer(customer_type), items, **kwargs)


# --- descontos por tipo de cliente ---

def test_employee_customer_receives_20_percent_discount():
    result = order("employee", [make_item(100, weight=1)])

    assert result["discount"] == 20
    assert result["shipping"] == 20.4
    assert result["tax"] == 5.6
    assert result["total"] == 106.0


def test_vip_below_1000_receives_10_percent_discount():
    result = order("vip", [make_item(500)])

    assert result["discount"] == 50
    assert result["total"] == 481.5


def test_vip_from_1000_receives_15_percent_discount():
    assert order("vip", [make_item(1000)])["discount"] == 150


def test_regular_below_800_has_no_discount():
    assert order("regular", [make_item(799)])["discount"] == 0


def test_regular_from_800_receives_5_percent_discount():
    assert order("regular", [make_item(800)])["discount"] == 40


def test_unknown_customer_type_has_no_discount():
    assert order("visitor", [make_item(1000)])["discount"] == 0


# --- cupons ---

def test_promo10_gives_10_percent_extra_discount():
    assert order(items=[make_item(300)], coupon="PROMO10")["discount"] == 30


def test_promo20_is_ignored_below_500():
    assert order(items=[make_item(499)], coupon="PROMO20")["discount"] == 0


def test_promo20_applies_from_500():
    assert order(items=[make_item(500)], coupon="PROMO20")["discount"] == 100


def test_vip50_gives_fixed_50_to_vip_customer():
    result = order("vip", [make_item(400)], coupon="VIP50")

    assert result["discount"] == 90  # 10% de 400 + 50


def test_vip50_is_ignored_for_non_vip_customer():
    assert order("regular", [make_item(400)], coupon="VIP50")["discount"] == 0


def test_unknown_coupon_is_ignored():
    assert order(items=[make_item(400)], coupon="INVALIDO")["discount"] == 0


def test_coupon_is_case_sensitive_in_current_behavior():
    assert order(items=[make_item(400)], coupon="promo10")["discount"] == 0


def test_total_discount_is_limited_to_25_percent_of_subtotal():
    result = order("employee", [make_item(1000)], coupon="PROMO10")

    assert result["discount"] == 250  # 20% + 10% seria 300


# --- subtotal ---

def test_items_with_zero_or_negative_quantity_are_ignored_in_subtotal():
    items = [make_item(100, qty=1), make_item(50, qty=0), make_item(70, qty=-2)]

    assert order(items=items)["subtotal"] == 100


# --- frete ---

def test_shipping_is_free_from_500_without_express():
    assert order(items=[make_item(500, weight=10)])["shipping"] == 0


def test_shipping_is_charged_below_500_in_southeast_state():
    assert order(items=[make_item(499)], state="SP")["shipping"] == 20


def test_shipping_uses_weight_in_southeast_state():
    assert order(items=[make_item(100, weight=5)], state="RJ")["shipping"] == 22


def test_shipping_is_more_expensive_in_other_states():
    result = order(items=[make_item(100, weight=10)], state="BA")

    assert result["shipping"] == 41  # 35 + 10 * 0.6
    assert result["tax"] == 12
    assert result["total"] == 153


def test_express_shipping_multiplies_shipping_by_1_8():
    assert order(items=[make_item(100)], express=True)["shipping"] == 36


def test_express_shipping_is_charged_even_above_500():
    assert order(items=[make_item(500)], express=True)["shipping"] == 36


def test_items_without_weight_count_as_zero_weight():
    items = [{"name": "Livro", "price": 100, "qty": 1}]

    assert order(items=items)["shipping"] == 20


# --- impostos ---

@pytest.mark.parametrize(
    "state, expected_tax",
    [("MG", 7), ("SP", 9), ("RJ", 8), ("ES", 7), ("BA", 12)],
)
def test_tax_rate_depends_on_state(state, expected_tax):
    result = order(items=[make_item(100)], state=state)

    assert result["tax"] == expected_tax


def test_tax_is_calculated_over_discounted_value():
    result = order("employee", [make_item(100)], state="MG")

    assert result["tax"] == 5.6  # 7% de 80


# --- pontos de fidelidade ---

def test_vip_earns_one_point_per_5_reais():
    assert order("vip", [make_item(500)])["points"] == 96  # 481.5 / 5


def test_regular_earns_one_point_per_10_reais():
    assert order("regular", [make_item(500)])["points"] == 53  # 535 / 10


# --- produtos duplicados ---

def test_no_duplicate_products_returns_empty_list():
    items = [make_item(10, name="A"), make_item(10, name="B")]

    assert order(items=items)["duplicate_products"] == []


def test_duplicate_products_keep_order_of_first_appearance():
    items = [
        make_item(10, name="A"),
        make_item(10, name="B"),
        make_item(10, name="B"),
        make_item(10, name="A"),
    ]

    assert order(items=items)["duplicate_products"] == ["A", "B"]


def test_product_repeated_many_times_is_listed_once():
    items = [make_item(10, name="Mouse") for _ in range(3)]

    assert order(items=items)["duplicate_products"] == ["Mouse"]


# --- efeitos colaterais ---

def test_processed_order_is_stored_in_orders_history():
    legacy_checkout.ORDERS_PROCESSED.clear()

    result = order()

    assert legacy_checkout.ORDERS_PROCESSED == [result]


def test_order_summary_is_printed(capsys):
    order("employee", [make_item(100)])

    output = capsys.readouterr().out
    assert "Pedido processado para Cliente" in output
    assert "TOTAL:" in output
