"use client";

import { useState } from "react";

export function useConfirmAction() {
  const [open, setOpen] = useState(false);
  const [onConfirm, setOnConfirm] = useState<() => void>(() => () => {});

  function confirm(action: () => void) {
    setOnConfirm(() => action);
    setOpen(true);
  }

  function handleConfirm() {
    onConfirm();
    setOpen(false);
  }

  function handleCancel() {
    setOpen(false);
  }

  return {
    open,
    confirm,
    handleConfirm,
    handleCancel,
  };
}