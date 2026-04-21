import type { CartItem, CartState } from "@/features/orders/types/cart";
import {
  addCartItem,
  clearCart,
  getCart,
  removeCartItem,
  updateCartItemQuantity,
} from "@/features/orders/utils/cart-storage";

export function getCartState(): CartState {
  return getCart();
}

export function addItemToCart(item: CartItem): CartState {
  return addCartItem(item);
}

export function updateItemQuantity(
  productId: string,
  quantity: number,
): CartState {
  return updateCartItemQuantity(productId, quantity);
}

export function removeItemFromCart(productId: string): CartState {
  return removeCartItem(productId);
}

export function clearCartState() {
  clearCart();
}