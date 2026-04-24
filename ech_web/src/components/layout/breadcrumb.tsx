"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

function formatSegment(segment: string): string {
  return segment
    .replaceAll("-", " ")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function Breadcrumb() {
  const pathname = usePathname();

  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) {
    return null;
  }

  const items = segments.map((segment, index) => {
    const href = `/${segments.slice(0, index + 1).join("/")}`;
    const isLast = index === segments.length - 1;

    return {
      label: formatSegment(segment),
      href,
      isLast,
    };
  });

  return (
    <nav aria-label="Breadcrumb" className="text-sm text-slate-400">
      <ol className="flex flex-wrap items-center gap-2">
        <li>
          <Link href="/" className="transition hover:text-white">
            Home
          </Link>
        </li>

        {items.map((item) => (
          <li key={item.href} className="flex items-center gap-2">
            <span className="text-slate-600">/</span>

            {item.isLast ? (
              <span className="font-medium text-slate-200">{item.label}</span>
            ) : (
              <Link href={item.href} className="transition hover:text-white">
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}