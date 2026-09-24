"""Processamento de pedidos (checkout).

Refatorado sem alterar o comportamento: cada regra de negócio agora vive em
uma função própria, e os valores fixos foram trocados por constantes.
"""

from collections import Counter

ORDERS_PROCESSED = []

# --- Descontos por tipo de cliente ---
VIP_HIGH_DISCOUNT_MIN_SUBTOTAL = 1000
VIP_HIGH_DISCOUNT_RATE = 0.15
VIP_DISCOUNT_RATE = 0.10
EMPLOYEE_DISCOUNT_RATE = 0.20
REGULAR_DISCOUNT_MIN_SUBTOTAL = 800
REGULAR_DISCOUNT_RATE = 0.05

# --- Cupons ---
PROMO10_RATE = 0.10
PROMO20_RATE = 0.20
PROMO20_MIN_SUBTOTAL = 500
VIP50_FIXED_DISCOUNT = 50
MAX_DISCOUNT_RATE = 0.25

# --- Frete ---
FREE_SHIPPING_MIN_SUBTOTAL = 500
SOUTHEAST_STATES = {"MG", "SP", "RJ", "ES"}
SOUTHEAST_BASE_SHIPPING = 20
SOUTHEAST_SHIPPING_PER_KG = 0.4
OTHER_BASE_SHIPPING = 35
OTHER_SHIPPING_PER_KG = 0.6
EXPRESS_SHIPPING_MULTIPLIER = 1.8

# --- Impostos ---
TAX_RATES = {
    "MG": 0.07,
    "SP": 0.09,
    "RJ": 0.08,
    "ES": 0.07,
}
DEFAULT_TAX_RATE = 0.12

# --- Pontos de fidelidade ---
VIP_POINTS_DIVISOR = 5
DEFAULT_POINTS_DIVISOR = 10


def calculate_subtotal(items):
    """Soma preço * quantidade, ignorando itens com quantidade <= 0."""
    subtotal = 0
    for item in items:
        if item["qty"] > 0:
            subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_customer_discount(customer_type, subtotal):
    """Desconto de acordo com o tipo de cliente."""
    if customer_type == "vip":
        if subtotal >= VIP_HIGH_DISCOUNT_MIN_SUBTOTAL:
            return subtotal * VIP_HIGH_DISCOUNT_RATE
        return subtotal * VIP_DISCOUNT_RATE
    if customer_type == "employee":
        return subtotal * EMPLOYEE_DISCOUNT_RATE
    if customer_type == "regular" and subtotal >= REGULAR_DISCOUNT_MIN_SUBTOTAL:
        return subtotal * REGULAR_DISCOUNT_RATE
    return 0


def calculate_coupon_discount(coupon, customer_type, subtotal):
    """Desconto extra gerado pelo cupom (0 se o cupom não se aplica)."""
    if coupon == "PROMO10":
        return subtotal * PROMO10_RATE
    if coupon == "PROMO20" and subtotal >= PROMO20_MIN_SUBTOTAL:
        return subtotal * PROMO20_RATE
    if coupon == "VIP50" and customer_type == "vip":
        return VIP50_FIXED_DISCOUNT
    return 0


def calculate_discount(customer_type, coupon, subtotal):
    """Desconto total (cliente + cupom), limitado ao máximo permitido."""
    discount = calculate_customer_discount(customer_type, subtotal)
    discount += calculate_coupon_discount(coupon, customer_type, subtotal)
    return min(discount, subtotal * MAX_DISCOUNT_RATE)


def calculate_total_weight(items):
    """Peso total do pedido (itens sem peso contam como 0)."""
    weight = 0
    for item in items:
        weight += item.get("weight", 0) * item["qty"]
    return weight


def calculate_shipping(subtotal, weight, state, express):
    """Frete por região e peso; grátis acima do mínimo, exceto no expresso."""
    if subtotal >= FREE_SHIPPING_MIN_SUBTOTAL and not express:
        return 0

    if state in SOUTHEAST_STATES:
        shipping = SOUTHEAST_BASE_SHIPPING + weight * SOUTHEAST_SHIPPING_PER_KG
    else:
        shipping = OTHER_BASE_SHIPPING + weight * OTHER_SHIPPING_PER_KG

    if express:
        shipping *= EXPRESS_SHIPPING_MULTIPLIER
    return shipping


def calculate_tax(amount, state):
    """Imposto sobre o valor já com desconto, conforme o estado."""
    return amount * TAX_RATES.get(state, DEFAULT_TAX_RATE)


def calculate_points(customer_type, total):
    """Pontos de fidelidade (VIP ganha o dobro)."""
    divisor = VIP_POINTS_DIVISOR if customer_type == "vip" else DEFAULT_POINTS_DIVISOR
    return int(total / divisor)


def find_duplicate_products(items):
    """Nomes de produtos que aparecem mais de uma vez, na ordem da 1ª aparição."""
    occurrences = Counter(item["name"] for item in items)
    duplicates = {name for name, count in occurrences.items() if count > 1}
    return [name for name in dict.fromkeys(occurrences) if name in duplicates]


def print_order_summary(customer_name, subtotal, discount, shipping, tax, total):
    print("Pedido processado para " + customer_name)
    print("Subtotal:", subtotal)
    print("Desconto:", discount)
    print("Frete:", shipping)
    print("Imposto:", tax)
    print("TOTAL:", total)


def process_order(customer, items, coupon="", state="MG", express=False):
    customer_type = customer["type"]

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(customer_type, coupon, subtotal)
    discounted_value = subtotal - discount
    shipping = calculate_shipping(
        subtotal, calculate_total_weight(items), state, express
    )
    tax = calculate_tax(discounted_value, state)
    grand_total = discounted_value + shipping + tax

    result = {
        "customer": customer["name"],
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "shipping": round(shipping, 2),
        "tax": round(tax, 2),
        "total": round(grand_total, 2),
        "points": calculate_points(customer_type, grand_total),
        "duplicate_products": find_duplicate_products(items),
    }

    ORDERS_PROCESSED.append(result)
    print_order_summary(
        customer["name"], subtotal, discount, shipping, tax, result["total"]
    )
    return result
