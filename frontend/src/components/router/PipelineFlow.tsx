import { PIPELINE_STAGES } from '../../utils/constants';
import { classNames } from '../../utils/helpers';
import { PipelineStage } from '../../types/task';

export type PipelineMode = 'idle' | 'live' | 'mini';

interface PipelineFlowProps {
  mode: PipelineMode;
  activeStage?: PipelineStage;
  completedStages?: PipelineStage[];
}

/**
 * The signature element of Aegis Router: the same User -> Router -> Planner ->
 * Registry -> Ranking -> Payment -> Execution -> Results pipeline, reused
 * everywhere (landing hero, sidebar rail, dashboard health, execution page)
 * so the orchestration story stays visually consistent across the whole app.
 */
export default function PipelineFlow({ mode, activeStage, completedStages = [] }: PipelineFlowProps) {
  const stages = PIPELINE_STAGES;
  const isMini = mode === 'mini';

  function stateFor(key: string) {
    if (completedStages.includes(key as PipelineStage)) return 'completed';
    if (activeStage === key) return 'running';
    return 'pending';
  }

  return (
    <div
      className={classNames(
        'flex items-center',
        isMini ? 'gap-1.5' : 'gap-2 md:gap-3 flex-wrap justify-center'
      )}
    >
      {stages.map((stage, i) => {
        const state = mode === 'idle' ? 'pending' : stateFor(stage.key);
        return (
          <div key={stage.key} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div
                className={classNames(
                  'rounded-full flex items-center justify-center border transition-all',
                  isMini ? 'h-2.5 w-2.5' : 'h-9 w-9 md:h-11 md:w-11',
                  state === 'completed' && 'bg-success/20 border-success text-success',
                  state === 'running' && 'bg-primary/20 border-primary text-primary animate-pulseNode',
                  state === 'pending' && 'bg-white/5 border-line text-ink-faint'
                )}
              >
                {!isMini && (
                  <span className="font-mono text-[10px] md:text-xs">{i + 1}</span>
                )}
              </div>
              {!isMini && (
                <span
                  className={classNames(
                    'text-[10px] md:text-xs font-mono uppercase tracking-wide',
                    state === 'pending' ? 'text-ink-faint' : 'text-ink-muted'
                  )}
                >
                  {stage.label}
                </span>
              )}
            </div>
            {i < stages.length - 1 && (
              <div
                className={classNames(
                  isMini ? 'w-3 h-px mx-0.5' : 'w-6 md:w-10 h-px mx-1 md:mx-2 mt-0 md:-mt-4',
                  state === 'completed' ? 'bg-success/60' : 'bg-line'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
