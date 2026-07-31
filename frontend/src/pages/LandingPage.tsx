import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Wallet, Users, BarChart3, ArrowRight } from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import PipelineFlow from '../components/router/PipelineFlow';
import AgentCard from '../components/marketplace/AgentCard';
import { MOCK_AGENTS } from '../services/agentService';

const FEATURES = [
  { icon: Zap, title: 'Intelligent Routing', body: 'Every task is planned, matched to a registry of live agents, and ranked before it ever runs.' },
  { icon: Wallet, title: 'x402 Payments', body: 'Agents get paid per task, settled on-chain the moment execution completes.' },
  { icon: Users, title: 'Multi-Agent Coordination', body: 'Complex requests fan out across specialists and get aggregated into one result.' },
  { icon: BarChart3, title: 'Analytics Dashboard', body: 'Track routing decisions, spend, and success rate across every agent you use.' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg grid-overlay">
      <Navbar />

      {/* Hero: the animated pipeline IS the thesis of the product */}
      <section className="relative px-6 pt-16 pb-20 text-center overflow-hidden">
        <div className="absolute inset-0 bg-grad-glow pointer-events-none" />
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative font-display text-4xl md:text-6xl font-semibold text-ink max-w-3xl mx-auto leading-tight"
        >
          The Operating System <span className="text-gradient">for AI Agents</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative mt-4 text-ink-muted text-sm md:text-base font-mono tracking-wide"
        >
          DISCOVER · ROUTE · PAY · EXECUTE · MONITOR
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="relative mt-3 text-ink-muted max-w-xl mx-auto"
        >
          Autonomous AI agents, coordinated through one intelligent router — from planning to payment to results.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="relative flex items-center justify-center gap-3 mt-8"
        >
          <Link to="/register" className="px-6 py-3 rounded-chip bg-grad-primary text-white text-sm font-medium hover:opacity-90 transition flex items-center gap-2">
            Launch Router <ArrowRight size={16} />
          </Link>
          <Link to="/marketplace" className="px-6 py-3 rounded-chip border border-line text-ink text-sm font-medium hover:border-primary/40 transition">
            Explore Marketplace
          </Link>
        </motion.div>

        {/* Signature element: full pipeline animation, idle state, the throughline for every other page */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="relative glass rounded-card mt-14 mx-auto max-w-4xl p-8 md:p-10"
        >
          <PipelineFlow mode="idle" />
          <p className="text-xs text-ink-faint font-mono mt-6">Every task moves through this exact pipeline, live, on the Execute page.</p>
        </motion.div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 max-w-6xl mx-auto">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="glass glass-hover rounded-card p-6"
            >
              <f.icon size={20} className="text-accent mb-3" />
              <h3 className="font-display text-ink mb-1.5">{f.title}</h3>
              <p className="text-sm text-ink-muted">{f.body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Marketplace preview */}
      <section className="px-6 py-16 max-w-6xl mx-auto">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="font-display text-2xl text-ink">Marketplace Preview</h2>
            <p className="text-sm text-ink-muted mt-1">A sample of agents the router can select from.</p>
          </div>
          <Link to="/marketplace" className="text-sm text-primary hover:underline hidden sm:inline">View all →</Link>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {MOCK_AGENTS.slice(0, 3).map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </section>

      {/* Workflow demo strip */}
      <section className="px-6 py-16 max-w-4xl mx-auto text-center">
        <h2 className="font-display text-2xl text-ink mb-3">How a task moves through Aegis Router</h2>
        <p className="text-sm text-ink-muted mb-8">User submits → Router plans → Registry finds agents → Ranking picks the best → Payment settles → Agents execute → Results return.</p>
        <div className="glass rounded-card p-8">
          <PipelineFlow mode="idle" />
        </div>
      </section>

      <Footer />
    </div>
  );
}
