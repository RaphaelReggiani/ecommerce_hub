"use client";

import { useState } from "react";

export function usePagination(initialPage = 1) {
  const [page, setPage] = useState(initialPage);

  function next() {
    setPage((p) => p + 1);
  }

  function prev() {
    setPage((p) => Math.max(1, p - 1));
  }

  function goTo(p: number) {
    setPage(Math.max(1, p));
  }

  return {
    page,
    setPage,
    next,
    prev,
    goTo,
  };
}