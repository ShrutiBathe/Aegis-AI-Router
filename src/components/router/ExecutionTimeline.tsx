import { PIPELINE_STAGES } from '../../utils/constants';
import { PipelineStage } from '../../types/task';
import { classNames } from '../../utils/helpers';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface ExecutionTimelineProps {
  activeStage: PipelineStage;
  completedStages: PipelineStage[];
}

export default function ExecutionTimeline({ activeStage, completedStages }: ExecutionTimelineProps) {
  return (
    <ol className="flex flex-col gap-3">
      {PIPELINE_STAGES.map((stage) => {
        const state = completedStages.includes(stage.key)
          ? 'completed'
          : activeStage === stage.key
          ? 'running'
          : 'pending';
        return (
          <li key={stage.key} className="flex items-center gap-3 text-sm">
            {state === 'completed' && <CheckCircle2 size={16} className="text-success" />}
            {state === 'running' && <Loader2 size={16} className="text-primary animate-spin" />}
            {state === 'pending' && <Circle size={16} className="text-ink-faint" />}
            <span className={classNames(state === 'pending' ? 'text-ink-faint' : 'text-ink')}>{stage.label}</span>
          </li>
        );
      })}
    </ol>
  );
}
