"use client";

import { useEffect } from "react";

type ConfirmActionDialogProps = {
  isOpen: boolean;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isPending?: boolean;
  tone?: "default" | "danger";
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmActionDialog({
  isOpen,
  title = "Confirm action",
  description = "Are you sure you want to continue with this action?",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isPending = false,
  tone = "default",
  onConfirm,
  onCancel,
}: ConfirmActionDialogProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape" && !isPending) {
        onCancel();
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, isPending, onCancel]);

  if (!isOpen) {
    return null;
  }

  const confirmButtonClass =
    tone === "danger"
      ? "bg-red-600 hover:bg-red-500"
      : "bg-blue-600 hover:bg-blue-500";

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center px-4">
      <button
        type="button"
        aria-label="Close dialog"
        onClick={isPending ? undefined : onCancel}
        className="absolute inset-0 bg-black/70"
      />

      <div className="relative z-10 w-full max-w-md rounded-3xl border border-slate-800 bg-slate-950 p-6 shadow-2xl">
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={isPending}
            className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isPending}
            className={`rounded-2xl px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60 ${confirmButtonClass}`}
          >
            {isPending ? "Processing..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}