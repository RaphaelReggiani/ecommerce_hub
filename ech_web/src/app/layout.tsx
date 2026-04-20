import "./globals.css";

import type { Metadata } from "next";

import { Footer } from "@/components/layout/app-footer";
import { Header } from "@/components/layout/app-header";
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
        <AppProvider>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </AppProvider>
      </body>
    </html>
  );
}