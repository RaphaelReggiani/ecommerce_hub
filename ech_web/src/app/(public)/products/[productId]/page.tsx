"use client";

import Image from "next/image";
import { useMemo, useState, type CSSProperties, type MouseEvent } from "react";
import { useParams, useRouter } from "next/navigation";

import { StockBadge } from "@/features/products/components/stock-badge";
import { useProduct } from "@/features/products/hooks/use-product";
import { useAppCart } from "@/providers/cart-provider";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const productId =
    typeof params.productId === "string" ? params.productId : "";

  const { data: product, isLoading, isError } = useProduct(productId);
  const { addItem, openCart } = useAppCart();

  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [zoomStyle, setZoomStyle] = useState<CSSProperties>({});
  const [isZooming, setIsZooming] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

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

  const selectedImage = galleryImages[selectedImageIndex] ?? null;

  function handleMouseMove(event: MouseEvent<HTMLDivElement>) {
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

  function buildCartItem() {
    if (!product) return null;

    return {
      product_id: product.id,
      name: product.name,
      brand: product.brand,
      product_type: product.product_type,
      main_image: product.main_image,
      unit_price: product.price,
      discount_price: product.discount_price,
      quantity: 1,
      max_quantity: product.inventory,
    };
  }

  function handleAddToCart() {
    if (!product || product.inventory <= 0) {
      setActionMessage("This product is currently out of stock.");
      return;
    }

    const cartItem = buildCartItem();

    if (!cartItem) return;

    addItem(cartItem);
    setActionMessage("Product added to cart.");
    openCart();
  }

  function handleBuyNow() {
    if (!product || product.inventory <= 0) {
      setActionMessage("This product is currently out of stock.");
      return;
    }

    const cartItem = buildCartItem();

    if (!cartItem) return;

    addItem(cartItem);
    router.push("/checkout");
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
                <div className="relative aspect-[4/3] w-full overflow-hidden">
                  <Image
                    src={selectedImage.src}
                    alt={selectedImage.alt}
                    fill
                    sizes="(max-width: 1024px) 100vw, 60vw"
                    className={`object-contain transition duration-200 ${
                      isZooming ? "cursor-zoom-in" : "cursor-default"
                    }`}
                    style={zoomStyle}
                    unoptimized
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
                      <div className="relative aspect-square h-full w-full">
                        <Image
                          src={image.src}
                          alt={image.alt}
                          fill
                          sizes="(max-width: 640px) 50vw, 25vw"
                          className="object-cover"
                          unoptimized
                        />
                      </div>
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

            {actionMessage && (
              <div className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300">
                {actionMessage}
              </div>
            )}

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={handleBuyNow}
                disabled={product.inventory <= 0}
                className="cursor-pointer rounded-2xl bg-blue-600 px-5 py-4 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Buy now
              </button>

              <button
                type="button"
                onClick={handleAddToCart}
                disabled={product.inventory <= 0}
                className="cursor-pointer rounded-2xl border border-slate-700 bg-slate-950 px-5 py-4 font-medium text-slate-200 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
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