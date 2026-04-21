import Link from "next/link";

export function UnauthorizedState() {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col items-center justify-center rounded-3xl border border-red-500/20 bg-red-500/10 px-6 py-12 text-center shadow-xl">
      <div className="space-y-4">
        <span className="inline-flex rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-red-300">
          Unauthorized
        </span>

        <h2 className="text-3xl font-semibold text-white">
          You do not have access to this area
        </h2>

        <p className="mx-auto max-w-xl text-sm leading-7 text-slate-300">
          Please sign in with an authorized account or return to the public
          area of the platform.
        </p>
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/login"
          className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Go to login
        </Link>

        <Link
          href="/"
          className="rounded-2xl border border-slate-700 bg-slate-950 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
        >
          Back to home
        </Link>
      </div>
    </div>
  );
}