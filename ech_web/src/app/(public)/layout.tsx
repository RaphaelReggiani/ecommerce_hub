"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

export default function PublicLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isAuthPage =
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/forgot-password" ||
    pathname === "/reset-password";

  if (isAuthPage) {
    return (
      <div className="flex min-h-[calc(100vh-140px)] items-center justify-center px-6 py-12">
        <div className="w-full max-w-6xl">{children}</div>
      </div>
    );
  }

  return <div className="min-h-screen bg-black text-gray-100">{children}</div>;
}