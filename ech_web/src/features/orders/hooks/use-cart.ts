"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  addItemToCart,
  clearCartState,
  getCartState,
  removeItemFromCart,
  updateItemQuantity,
} from "@/features/orders/api/cart";
import type { CartItem, CartState } from "@/features/orders/types/cart";

export function useCart() {
  const [cart, setCart] = useState<CartState>(() => getCartState());

  useEffect(() => {
    function handleCartUpdated() {
      setCart(getCartState());
    }

    window.addEventListener("ech-cart-updated", handleCartUpdated);

    return () => {
      window.removeEventListener("ech-cart-updated", handleCartUpdated);
    };
  }, []);

  const addItem = useCallback((item: CartItem) => {
    setCart(addItemToCart(item));
  }, []);

  const updateQuantity = useCallback((productId: string, quantity: number) => {
    setCart(updateItemQuantity(productId, quantity));
  }, []);

  const removeItem = useCallback((productId: string) => {
    setCart(removeItemFromCart(productId));
  }, []);

  const clear = useCallback(() => {
    clearCartState();
    setCart({ items: [] });
  }, []);

  const itemCount = useMemo(
    () => cart.items.reduce((total, item) => total + item.quantity, 0),
    [cart.items],
  );

  const subtotal = useMemo(
    () =>
      cart.items.reduce((total, item) => {
        const effectivePrice = Number(item.discount_price ?? item.unit_price);
        return total + effectivePrice * item.quantity;
      }, 0),
    [cart.items],
  );

  return {
    cart,
    items: cart.items,
    itemCount,
    subtotal,
    addItem,
    updateQuantity,
    removeItem,
    clear,
  };
}