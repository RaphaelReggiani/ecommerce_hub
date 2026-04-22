"use client";

import { useState } from "react";

import { ConfirmActionDialog } from "@/components/shared/confirm-action-dialog";
import { useCancelShipment } from "@/features/shipping/hooks/use-cancel-shipment";
import { useProcessShipment } from "@/features/shipping/hooks/use-process-shipment";
import type { ShipmentManagementDetail, ShipmentStatus } from "@/features/shipping/types/shipment";
import { ApiClientError } from "@/lib/api/error-handler";

type ShipmentActionsProps = {
  shipment: ShipmentManagementDetail;
};

const processTargets: ShipmentStatus[] = [
  "preparing",
  "ready_to_ship",
  "shipped",
  "in_transit",
  "out_for_delivery",
  "delivered",
  "failed",
  "returned",
];

export function ShipmentActions({ shipment }: ShipmentActionsProps) {
  const processMutation = useProcessShipment(shipment.id);
  const cancelMutation = useCancelShipment(shipment.id);

  const [selectedStatus, setSelectedStatus] = useState<ShipmentStatus | null>(null);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleProcessConfirm() {
    if (!selectedStatus) return;

    setActionError(null);

    try {
      await processMutation.mutateAsync({ new_status: selectedStatus });
      setSelectedStatus(null);
    } catch (error) {
      if (error instanceof ApiClientError) {
        setActionError(error.message);
        return;
      }

      setActionError("Unable to update shipment status right now.");
    }
  }

  async function handleCancelConfirm() {
    setActionError(null);

    try {
      await cancelMutation.mutateAsync({});
      setConfirmCancel(false);
    } catch (error) {
      if (error instanceof ApiClientError) {
        setActionError(error.message);
        return;
      }

      setActionError("Unable to cancel shipment right now.");
    }
  }

  const isPending = processMutation.isPending || cancelMutation.isPending;

  return (
    <>
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Actions
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">
            Shipment operations
          </h3>
        </div>

        {actionError ? (
          <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {actionError}
          </div>
        ) : null}

        <div className="flex flex-wrap gap-3">
          {processTargets.map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => setSelectedStatus(status)}
              className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
            >
              Set {status.replaceAll("_", " ")}
            </button>
          ))}

          <button
            type="button"
            onClick={() => setConfirmCancel(true)}
            className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/20"
          >
            Cancel shipment
          </button>
        </div>
      </div>

      <ConfirmActionDialog
        isOpen={Boolean(selectedStatus)}
        title="Confirm shipment status update"
        description="This action will update the shipment lifecycle. Confirm to continue."
        confirmLabel="Confirm"
        cancelLabel="Back"
        isPending={isPending}
        onConfirm={handleProcessConfirm}
        onCancel={() => setSelectedStatus(null)}
      />

      <ConfirmActionDialog
        isOpen={confirmCancel}
        title="Confirm shipment cancellation"
        description="This action will cancel the shipment. Confirm to continue."
        confirmLabel="Cancel shipment"
        cancelLabel="Back"
        isPending={isPending}
        tone="danger"
        onConfirm={handleCancelConfirm}
        onCancel={() => setConfirmCancel(false)}
      />
    </>
  );
}