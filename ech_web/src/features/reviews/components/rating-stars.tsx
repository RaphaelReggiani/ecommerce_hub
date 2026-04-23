type RatingStarsProps = {
  rating: number;
  size?: "sm" | "md";
};

export function RatingStars({
  rating,
  size = "md",
}: RatingStarsProps) {
  const stars = [1, 2, 3, 4, 5];
  const sizeClass = size === "sm" ? "text-sm" : "text-lg";

  return (
    <div className={`flex items-center gap-1 ${sizeClass}`}>
      {stars.map((star) => (
        <span
          key={star}
          className={star <= rating ? "text-amber-400" : "text-slate-600"}
        >
          ★
        </span>
      ))}
    </div>
  );
}