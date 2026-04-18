"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl text-center">
        <h1 className="text-xl font-semibold text-red-500">
          Something went wrong
        </h1>

        <p className="mt-3 text-sm text-slate-400">
          An unexpected error occurred.
        </p>

        <button
          onClick={() => reset()}
          className="mt-6 rounded-xl bg-blue-600 px-5 py-3 text-white hover:bg-blue-500"
        >
          Try again
        </button>
      </div>
    </div>
  );
}