"use client";

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { CartDrawer } from "@/features/orders/components/cart-drawer";
import { useCart } from "@/features/orders/hooks/use-cart";

type CartContextValue = ReturnType<typeof useCart> & {
  isCartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  toggleCart: () => void;
};

const CartContext = createContext<CartContextValue | null>(null);

type CartProviderProps = {
  children: ReactNode;
};

export function CartProvider({ children }: CartProviderProps) {
  const cart = useCart();
  const [isCartOpen, setIsCartOpen] = useState(false);

  function openCart() {
    setIsCartOpen(true);
  }

  function closeCart() {
    setIsCartOpen(false);
  }

  function toggleCart() {
    setIsCartOpen((current) => !current);
  }

  function handleIncrease(productId: string) {
    const item = cart.items.find((entry) => entry.product_id === productId);

    if (!item) return;

    cart.updateQuantity(productId, item.quantity + 1);
  }

  function handleDecrease(productId: string) {
    const item = cart.items.find((entry) => entry.product_id === productId);

    if (!item) return;

    cart.updateQuantity(productId, item.quantity - 1);
  }

  const value = useMemo<CartContextValue>(
    () => ({
      ...cart,
      isCartOpen,
      openCart,
      closeCart,
      toggleCart,
    }),
    [cart, isCartOpen],
  );

  return (
    <CartContext.Provider value={value}>
      {children}

      <CartDrawer
        isOpen={isCartOpen}
        items={cart.items}
        subtotal={cart.subtotal}
        onClose={closeCart}
        onIncrease={handleIncrease}
        onDecrease={handleDecrease}
        onRemove={cart.removeItem}
      />
    </CartContext.Provider>
  );
}

export function useAppCart() {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error("useAppCart must be used within a CartProvider");
  }

  return context;
}