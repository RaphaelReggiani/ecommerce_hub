"use client";

import { useRouter, useSearchParams } from "next/navigation";

export function useQueryParams() {
  const router = useRouter();
  const params = useSearchParams();

  function setParam(key: string, value: string) {
    const newParams = new URLSearchParams(params.toString());
    newParams.set(key, value);
    router.push(`?${newParams.toString()}`);
  }

  function removeParam(key: string) {
    const newParams = new URLSearchParams(params.toString());
    newParams.delete(key);
    router.push(`?${newParams.toString()}`);
  }

  return {
    params,
    setParam,
    removeParam,
  };
}