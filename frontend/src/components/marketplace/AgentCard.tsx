import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Target } from 'lucide-react';
import { Agent } from '../../types/agent';
import RatingBadge from './RatingBadge';
import { formatCurrency, formatLatency, formatPercent } from '../../utils/formatters';

// Surfaces the ranking signals (speed, cost, rating) the router itself would
// weigh, so browsing the marketplace already primes the "ranking" concept.
export default function AgentCard({ agent }: { agent: Agent }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass glass-hover rounded-card p-5 flex flex-col gap-3"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div
            className="h-10 w-10 rounded-card flex items-center justify-center font-display text-white text-sm"
            style={{ background: agent.avatarColor }}
          >
            {agent.name.slice(0, 1)}
          </div>
          <div>
            <p className="text-ink font-medium">{agent.name}</p>
            <p className="text-xs text-ink-faint">{agent.owner}</p>
          </div>
        </div>
        <span className={`h-2 w-2 rounded-full mt-1 ${agent.online ? 'bg-success' : 'bg-ink-faint'}`} />
      </div>

      <p className="text-sm text-ink-muted line-clamp-2">{agent.description}</p>

      <div className="flex items-center gap-3 text-xs">
        <RatingBadge rating={agent.rating} />
        <span className="text-ink-faint">·</span>
        <span className="text-ink-muted">{formatPercent(agent.accuracy)} accuracy</span>
        <span className="text-ink-faint">·</span>
        <span className="text-ink-muted">{formatLatency(agent.latencyMs)}</span>
      </div>

      <div className="flex items-center gap-2 text-[11px] text-ink-faint">
        <Zap size={12} className="text-accent" /> fast
        <Target size={12} className="text-secondary ml-2" /> accurate
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-line">
        <span className="font-display text-ink">{formatCurrency(agent.price)}</span>
        <Link
          to={`/marketplace/${agent.id}`}
          className="px-4 py-1.5 rounded-chip bg-grad-primary text-white text-xs font-medium hover:opacity-90 transition"
        >
          Try Agent
        </Link>
      </div>
    </motion.div>
  );
}
