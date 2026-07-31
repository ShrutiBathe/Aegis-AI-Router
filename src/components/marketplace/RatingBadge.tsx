import { Star } from 'lucide-react';

export default function RatingBadge({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-warning">
      <Star size={12} fill="currentColor" />
      {rating.toFixed(1)}
    </span>
  );
}
