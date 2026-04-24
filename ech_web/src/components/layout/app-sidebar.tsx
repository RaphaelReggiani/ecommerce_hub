"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { sidebarNavigation, type NavigationItem } from "@/config/navigation";
import { hasRequiredRole } from "@/lib/auth/route-guards";

type AppSidebarProps = {
  userRole: string | null | undefined;
};

function isActivePath(pathname: string, item: NavigationItem): boolean {
  if (item.exact) {
    return pathname === item.href;
  }

  return pathname === item.href || pathname.startsWith(`${item.href}/`);
}

function canShowItem(item: NavigationItem, userRole: string | null | undefined) {
  if (!item.requiredRoles || item.requiredRoles.length === 0) {
    return true;
  }

  return hasRequiredRole(userRole, item.requiredRoles);
}

export function AppSidebar({ userRole }: AppSidebarProps) {
  const pathname = usePathname();

  const navigation: NavigationItem[] = sidebarNavigation.admin.filter(
    (item: NavigationItem) => canShowItem(item, userRole),
  );

  return (
    <aside className="hidden w-72 shrink-0 lg:block">
      <div className="sticky top-24 rounded-3xl border border-slate-800 bg-slate-950/80 p-5 shadow-2xl">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-blue-400">
            Admin
          </p>
          <h2 className="mt-2 text-lg font-semibold text-white">
            Control Center
          </h2>
        </div>

        <nav className="space-y-2">
          {navigation.map((item: NavigationItem) => {
            const active = isActivePath(pathname, item);

            const visibleChildren: NavigationItem[] = item.children
              ? item.children.filter((child: NavigationItem) =>
                  canShowItem(child, userRole),
                )
              : [];

            return (
              <div key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition ${
                    active
                      ? "bg-blue-600 text-white"
                      : "text-slate-300 hover:bg-slate-900 hover:text-white"
                  }`}
                >
                  {item.label}
                </Link>

                {visibleChildren.length > 0 && active && (
                  <div className="mt-2 space-y-1 border-l border-slate-800 pl-3">
                    {visibleChildren.map((child: NavigationItem) => {
                      const childActive = isActivePath(pathname, child);

                      return (
                        <Link
                          key={child.href}
                          href={child.href}
                          className={`block rounded-xl px-3 py-2 text-sm transition ${
                            childActive
                              ? "bg-slate-800 text-white"
                              : "text-slate-400 hover:bg-slate-900 hover:text-white"
                          }`}
                        >
                          {child.label}
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}