import Link from "next/link";

export default function HomePage() {
  const featuredCategories = [
    {
      title: "Phones",
      description: "Premium smartphones with performance, camera quality, and modern design.",
      href: "/products?product_type=PHONE",
    },
    {
      title: "Headsets",
      description: "Immersive audio for gaming, work, and entertainment.",
      href: "/products?product_type=HEADSET",
    },
    {
      title: "Keyboards",
      description: "Mechanical and wireless options for productivity and gaming.",
      href: "/products?product_type=KEYBOARD",
    },
    {
      title: "Mice",
      description: "Precision, speed, and comfort for every workflow.",
      href: "/products?product_type=MOUSE",
    },
  ];

  const highlights = [
    "Premium electronics and peripherals",
    "Curated catalog managed by staff",
    "Modern shopping experience",
    "Selected offers and featured products",
  ];

  const promoCards = [
    {
      eyebrow: "Featured deal",
      title: "Save up to 15%",
      description:
        "Explore selected devices with promotional pricing for work, gaming, and entertainment.",
    },
    {
      eyebrow: "Fast shopping",
      title: "Browse by category",
      description:
        "Find phones, audio, keyboards, mice, and more through a focused and easy-to-navigate catalog.",
    },
    {
      eyebrow: "Customer access",
      title: "Create your account",
      description:
        "Register to start shopping, manage your profile, and continue toward checkout.",
    },
  ];

  return (
    <div className="min-h-screen bg-black text-gray-100">
      <section className="px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <div className="mx-auto grid max-w-screen-2xl gap-8 rounded-[2rem] border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-8 shadow-2xl lg:grid-cols-[1.15fr_0.85fr] lg:p-12">
          <div className="space-y-8">
            <div className="space-y-4">
              <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
                E-Commerce Hub
              </span>

              <h1 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-5xl xl:text-6xl">
                Premium electronics and peripherals for a modern shopping experience
              </h1>

              <p className="max-w-2xl text-base leading-8 text-slate-300 md:text-lg">
                Discover selected phones, headsets, keyboards, mice, microphones,
                and other devices curated for performance, design, and everyday use.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/products"
                className="rounded-2xl bg-blue-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
              >
                Explore products
              </Link>

            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {highlights.map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-4 text-sm text-slate-300"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4">
            {promoCards.map((card) => (
              <div
                key={card.title}
                className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6"
              >
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
                  {card.eyebrow}
                </p>
                <h2 className="mt-3 text-2xl font-semibold text-white">
                  {card.title}
                </h2>
                <p className="mt-3 text-sm leading-7 text-slate-400">
                  {card.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-4 sm:px-6 lg:px-8 lg:py-6">
        <div className="mx-auto max-w-screen-2xl">
          <div className="grid gap-6 lg:grid-cols-4">
            {featuredCategories.map((category) => (
              <Link
                key={category.title}
                href={category.href}
                className="group rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl transition hover:-translate-y-1 hover:border-blue-500/40 hover:bg-slate-900"
              >
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-slate-500">
                  Category
                </p>
                <h3 className="mt-3 text-2xl font-semibold text-white transition group-hover:text-blue-300">
                  {category.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-400">
                  {category.description}
                </p>
                <div className="mt-6 inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition group-hover:border-blue-500 group-hover:text-white">
                  Shop category
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <div className="mx-auto max-w-screen-2xl rounded-[2rem] border border-slate-800 bg-slate-900/70 p-8 shadow-2xl lg:p-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
                Start shopping
              </p>
              <h2 className="mt-3 text-3xl font-semibold text-white md:text-4xl">
                Ready to explore the catalog?
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-8 text-slate-400">
                Visit the products page to browse the catalog, filter by category,
                search by brand, and open full product pages with gallery, pricing,
                stock visibility, and purchase-oriented actions.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/products"
                className="rounded-2xl bg-blue-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
              >
                Go to catalog
              </Link>

              <Link
                href="/register"
                className="rounded-2xl border border-slate-700 bg-slate-950 px-6 py-3 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
              >
                Create account
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}