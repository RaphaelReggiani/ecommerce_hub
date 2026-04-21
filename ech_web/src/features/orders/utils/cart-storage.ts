import type { CartItem, CartState } from "@/features/orders/types/cart";

const CART_STORAGE_KEY = "ech-cart";

function isBrowser() {
  return typeof window !== "undefined";
}

function emitCartUpdate() {
  if (!isBrowser()) return;
  window.dispatchEvent(new Event("ech-cart-updated"));
}

export function getCart(): CartState {
  if (!isBrowser()) {
    return { items: [] };
  }

  const raw = window.localStorage.getItem(CART_STORAGE_KEY);

  if (!raw) {
    return { items: [] };
  }

  try {
    const parsed = JSON.parse(raw) as CartState;

    if (!parsed || !Array.isArray(parsed.items)) {
      return { items: [] };
    }

    return parsed;
  } catch {
    return { items: [] };
  }
}

export function saveCart(cart: CartState) {
  if (!isBrowser()) return;

  window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  emitCartUpdate();
}

export function clearCart() {
  if (!isBrowser()) return;

  window.localStorage.removeItem(CART_STORAGE_KEY);
  emitCartUpdate();
}

export function addCartItem(item: CartItem): CartState {
  const cart = getCart();

  if (!item || !item.product_id) {
    return cart;
  }

  const existingItem = cart.items.find(
    (cartItem) => cartItem.product_id === item.product_id,
  );

  if (existingItem) {
    const nextQuantity = existingItem.quantity + item.quantity;

    existingItem.quantity = item.max_quantity
      ? Math.min(nextQuantity, item.max_quantity)
      : nextQuantity;
  } else {
    cart.items.push({
      ...item,
      quantity: item.quantity > 0 ? item.quantity : 1,
    });
  }

  saveCart(cart);
  return cart;
}

export function updateCartItemQuantity(
  productId: string,
  quantity: number,
): CartState {
  const cart = getCart();

  cart.items = cart.items
    .map((item) =>
      item.product_id === productId
        ? {
            ...item,
            quantity:
              item.max_quantity && quantity > item.max_quantity
                ? item.max_quantity
                : quantity,
          }
        : item,
    )
    .filter((item) => item.quantity > 0);

  saveCart(cart);
  return cart;
}

export function removeCartItem(productId: string): CartState {
  const cart = getCart();

  cart.items = cart.items.filter((item) => item.product_id !== productId);

  saveCart(cart);
  return cart;
}

export function getCartItemCount() {
  const cart = getCart();

  return cart.items.reduce((total, item) => total + item.quantity, 0);
}

export function getCartSubtotal() {
  const cart = getCart();

  return cart.items.reduce((total, item) => {
    const price = Number(item.discount_price ?? item.unit_price);

    if (Number.isNaN(price)) {
      return total;
    }

    return total + price * item.quantity;
  }, 0);
}