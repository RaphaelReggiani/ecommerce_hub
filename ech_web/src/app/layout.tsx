import "./globals.css";

import type { Metadata } from "next";

import { AppProvider } from "@/providers/app-provider";

export const metadata: Metadata = {
  title: "E-Commerce Hub",
  description: "Modern E-Commerce platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black text-white antialiased">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}