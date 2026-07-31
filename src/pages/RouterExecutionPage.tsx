import { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import WorkflowGraph from '../components/router/WorkflowGraph';
import LiveLogs from '../components/router/LiveLogs';
import ProgressTracker from '../components/router/ProgressTracker';
import SelectedAgentCard from '../components/router/SelectedAgentCard';
import { PipelineStage } from '../types/task';
import { PIPELINE_STAGES } from '../utils/constants';
import { MOCK_AGENTS } from '../services/agentService';

const STAGE_LOGS: Record<PipelineStage, string> = {
  router: 'Task received by router.',
  planner: 'Planning execution steps.',
  registry: 'Searching registry — found 6 agents.',
  ranking: 'Ranking complete — scoring speed, cost, accuracy.',
  payment: 'Processing x402 payment.',
  execution: 'Executing on selected agent.',
  results: 'Aggregating and returning results.',
};

export default function RouterExecutionPage() {
  const location = useLocation();
  const prompt = (location.state as { prompt?: string })?.prompt ?? 'Build a startup pitch deck';
  const selectedAgent = MOCK_AGENTS[2]; // Presentation AI, matches the demo prompt

  const [stageIndex, setStageIndex] = useState(0);
  const [completed, setCompleted] = useState<PipelineStage[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    let i = 0;
    const interval = setInterval(() => {
      const stage = PIPELINE_STAGES[i];
      setStageIndex(i);
      setLogs((prev) => [...prev, STAGE_LOGS[stage.key]]);
      setCompleted((prev) => (i > 0 ? [...prev, PIPELINE_STAGES[i - 1].key] : prev));

      if (i === PIPELINE_STAGES.length - 1) {
        clearInterval(interval);
        setTimeout(() => {
          setCompleted((prev) => [...prev, stage.key]);
          setLogs((prev) => [...prev, 'Completed.']);
        }, 900);
      }
      i += 1;
    }, 1100);

    return () => clearInterval(interval);
  }, []);

  const activeStage = PIPELINE_STAGES[stageIndex].key;
  const percent = Math.min(100, Math.round(((completed.length) / PIPELINE_STAGES.length) * 100));

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl text-ink mb-1">Router Execution</h1>
        <p className="text-sm text-ink-muted font-mono">"{prompt}"</p>
      </div>

      <WorkflowGraph activeStage={activeStage} completedStages={completed} />

      <ProgressTracker percent={percent} />

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h2 className="font-display text-lg text-ink mb-3">Live Logs</h2>
          <LiveLogs logs={logs} />
        </div>
        <SelectedAgentCard agent={selectedAgent} score={97.2} />
      </div>
    </div>
  );
}
