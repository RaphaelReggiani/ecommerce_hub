export function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950/80">
      <div className="mx-auto flex max-w-screen-2xl flex-col gap-3 px-4 py-6 text-sm text-slate-400 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-semibold text-slate-200">ECH Innovations</p>
          <p className="mt-1">Premium electronics and peripherals platform.</p>
        </div>

        <div className="text-xs text-slate-500">
          © {new Date().getFullYear()} ECH Innovations. All rights reserved.
        </div>
      </div>
    </footer>
  );
}