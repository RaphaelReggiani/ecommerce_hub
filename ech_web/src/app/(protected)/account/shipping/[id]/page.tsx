"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { routes } from "@/config/routes";
import { ShipmentDetailCard } from "@/features/shipping/components/shipment-detail-card";
import { ShipmentStatusBadge } from "@/features/shipping/components/shipment-status-badge";
import { ShipmentTimeline } from "@/features/shipping/components/shipment-timeline";
import { useShipment } from "@/features/shipping/hooks/use-shipment";
import { formatDateTime } from "@/lib/utils/format-date";

export default function AccountShipmentDetailPage() {
  const params = useParams<{ id: string }>();
  const shipmentId = params?.id;
  const { data, isLoading, isError, refetch } = useShipment(shipmentId);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading shipment..."
          description="Please wait while we load the shipment details."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load shipment."
          description="We could not retrieve this shipment right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Shipment detail"
        title={`Shipment ${data.id.slice(0, 8)}...`}
        description="Review the shipment summary, delivery timeline, and tracking history."
        actions={
          <Link
            href={routes.protected.shipping}
            className="inline-flex items-center rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
          >
            Back to shipping
          </Link>
        }
      />

      <ShipmentDetailCard shipment={data} />

      <ShipmentTimeline lifecycle={data.lifecycle} />

      {!!data.tracking_updates.length && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Tracking
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Tracking updates
            </h2>
          </div>

          <div className="space-y-4">
            {data.tracking_updates.map((update) => (
              <div
                key={update.id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">
                      {update.description}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {update.location || "Location unavailable"}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {formatDateTime(update.event_at)}
                    </p>
                  </div>

                  <div>
                    {update.status ? (
                      <ShipmentStatusBadge status={update.status} />
                    ) : null}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!!data.visible_notes.length && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Notes
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Shipment notes
            </h2>
          </div>

          <div className="space-y-4">
            {data.visible_notes.map((note) => (
              <div
                key={note.id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-sm text-slate-200">{note.message}</p>
                <p className="mt-2 text-xs text-slate-500">
                  {note.author_name || "System"} • {formatDateTime(note.created_at)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!!data.events.length && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Events
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Shipment events
            </h2>
          </div>

          <div className="space-y-4">
            {data.events.map((event) => (
              <div
                key={event.id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-sm capitalize text-white">
                  {event.event_type.replaceAll("_", " ")}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {event.performed_by_name || "System"} • {formatDateTime(event.created_at)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageContainer>
  );
}