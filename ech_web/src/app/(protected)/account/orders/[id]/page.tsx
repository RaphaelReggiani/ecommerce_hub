"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { StockBadge } from "@/features/products/components/stock-badge";
import { useProduct } from "@/features/products/hooks/use-product";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

export default function ProductDetailPage() {
  const params = useParams();
  const productId =
    typeof params.productId === "string" ? params.productId : "";

  const { data: product, isLoading, isError } = useProduct(productId);

  const galleryImages = useMemo(() => {
    if (!product) return [];

    const imagesFromApi =
      product.images?.map((image) => ({
        id: image.id,
        src: image.image,
        alt: `${product.name} image ${image.order}`,
      })) ?? [];

    if (imagesFromApi.length > 0) {
      return imagesFromApi;
    }

    if (product.main_image) {
      return [
        {
          id: "main-image",
          src: product.main_image,
          alt: product.name,
        },
      ];
    }

    return [];
  }, [product]);

  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [zoomStyle, setZoomStyle] = useState<React.CSSProperties>({});
  const [isZooming, setIsZooming] = useState(false);

  const selectedImage = galleryImages[selectedImageIndex] ?? null;

  function handleMouseMove(
    event: React.MouseEvent<HTMLDivElement, MouseEvent>,
  ) {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;

    setIsZooming(true);
    setZoomStyle({
      transformOrigin: `${x}% ${y}%`,
      transform: "scale(1.9)",
    });
  }

  function handleMouseLeave() {
    setIsZooming(false);
    setZoomStyle({
      transformOrigin: "center center",
      transform: "scale(1)",
    });
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-screen-2xl rounded-3xl border border-slate-800 bg-slate-900/70 p-12 text-center text-slate-400 shadow-xl">
          Loading product...
        </div>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="min-h-screen bg-black px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-screen-2xl rounded-3xl border border-red-500/20 bg-red-500/10 p-12 text-center text-red-300 shadow-xl">
          Unable to load this product.
        </div>
      </div>
    );
  }

  const hasDiscount =
    product.discount_price !== null &&
    Number(product.discount_price) < Number(product.price);

  return (
    <div className="min-h-screen bg-black px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-screen-2xl space-y-8">
        <section className="grid gap-8 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl lg:grid-cols-[1.1fr_0.9fr] lg:p-8">
          <div className="space-y-6">
            <div
              className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-950"
              onMouseMove={selectedImage ? handleMouseMove : undefined}
              onMouseLeave={selectedImage ? handleMouseLeave : undefined}
            >
              {selectedImage ? (
                <div className="aspect-[4/3] w-full overflow-hidden">
                  <img
                    src={selectedImage.src}
                    alt={selectedImage.alt}
                    className={`h-full w-full object-contain transition duration-200 ${
                      isZooming ? "cursor-zoom-in" : "cursor-default"
                    }`}
                    style={zoomStyle}
                  />
                </div>
              ) : (
                <div className="flex aspect-[4/3] items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-slate-500">
                  No image available
                </div>
              )}
            </div>

            {galleryImages.length > 0 && (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {galleryImages.map((image, index) => {
                  const isSelected = index === selectedImageIndex;

                  return (
                    <button
                      key={image.id}
                      type="button"
                      onClick={() => setSelectedImageIndex(index)}
                      className={`overflow-hidden rounded-2xl border bg-slate-950 transition ${
                        isSelected
                          ? "border-blue-500 shadow-[0_0_0_1px_rgba(59,130,246,0.4)]"
                          : "border-slate-800 hover:border-slate-600"
                      }`}
                    >
                      <img
                        src={image.src}
                        alt={image.alt}
                        className="aspect-square h-full w-full object-cover"
                      />
                    </button>
                  );
                })}
              </div>
            )}

            <div className="rounded-3xl border border-slate-800 bg-slate-950 p-6">
              <h2 className="mb-3 text-xl font-semibold text-white">
                Description
              </h2>
              <p className="leading-8 text-slate-300">{product.description}</p>
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-950 p-6">
              <h2 className="mb-3 text-xl font-semibold text-white">
                Technical information
              </h2>
              <p className="whitespace-pre-line leading-8 text-slate-300">
                {product.technical_information}
              </p>
            </div>
          </div>

          <div className="flex flex-col space-y-6">
            <div className="space-y-4">
              <p className="text-xs font-medium uppercase tracking-[0.22em] text-blue-400">
                {product.product_type}
              </p>

              <h1 className="text-3xl font-semibold leading-tight text-white md:text-4xl">
                {product.name}
              </h1>

              <p className="text-sm text-slate-400">
                Brand: <span className="text-slate-200">{product.brand}</span>
              </p>

              <StockBadge inventory={product.inventory} />
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-950 p-6">
              <div className="flex flex-wrap items-end gap-3">
                {hasDiscount ? (
                  <>
                    <span className="text-4xl font-semibold text-blue-400">
                      {formatCurrency(product.discount_price)}
                    </span>
                    <span className="text-lg text-slate-500 line-through">
                      {formatCurrency(product.price)}
                    </span>
                  </>
                ) : (
                  <span className="text-4xl font-semibold text-blue-400">
                    {formatCurrency(product.price)}
                  </span>
                )}
              </div>

              <p className="mt-4 text-sm leading-6 text-slate-400">
                Product published on {formatDateTime(product.created_at)}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                className="rounded-2xl bg-blue-600 px-5 py-4 font-medium cursor-pointer text-white transition hover:bg-blue-500"
              >
                Buy now
              </button>

              <button
                type="button"
                className="rounded-2xl border border-slate-700 bg-slate-950 px-5 py-4 font-medium text-slate-200 cursor-pointer transition hover:border-blue-500 hover:text-white"
              >
                Add to cart
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}