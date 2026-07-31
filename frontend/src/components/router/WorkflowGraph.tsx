import { useMemo } from 'react';
import ReactFlow, { Background, Edge, Node, Position } from 'reactflow';
import 'reactflow/dist/style.css';
import { PIPELINE_STAGES } from '../../utils/constants';
import { PipelineStage } from '../../types/task';

interface WorkflowGraphProps {
  activeStage: PipelineStage;
  completedStages: PipelineStage[];
}

const STATUS_COLORS: Record<string, { border: string; bg: string; text: string }> = {
  completed: { border: '#22C55E', bg: 'rgba(34,197,94,0.12)', text: '#22C55E' },
  running: { border: '#3B82F6', bg: 'rgba(59,130,246,0.14)', text: '#60A5FA' },
  pending: { border: 'rgba(148,163,184,0.25)', bg: 'rgba(255,255,255,0.03)', text: '#64748B' },
};

export default function WorkflowGraph({ activeStage, completedStages }: WorkflowGraphProps) {
  const { nodes, edges } = useMemo(() => {
    const allStages = [{ key: 'user', label: 'User' }, ...PIPELINE_STAGES];

    const nodes: Node[] = allStages.map((stage, i) => {
      const state =
        stage.key === 'user'
          ? 'completed'
          : completedStages.includes(stage.key as PipelineStage)
          ? 'completed'
          : activeStage === stage.key
          ? 'running'
          : 'pending';
      const colors = STATUS_COLORS[state];

      return {
        id: stage.key,
        position: { x: (i % 4) * 220, y: Math.floor(i / 4) * 130 },
        data: { label: stage.label },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        style: {
          background: colors.bg,
          border: `1.5px solid ${colors.border}`,
          borderRadius: 12,
          color: colors.text,
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 13,
          padding: '10px 16px',
          boxShadow: state === 'running' ? `0 0 16px ${colors.border}` : 'none',
        },
      };
    });

    const edges: Edge[] = [];
    for (let i = 0; i < allStages.length - 1; i++) {
      const fromKey = allStages[i].key;
      const toKey = allStages[i + 1].key;
      const isLive =
        completedStages.includes(fromKey as PipelineStage) || fromKey === 'user'
          ? activeStage === toKey || completedStages.includes(toKey as PipelineStage)
          : false;
      edges.push({
        id: `${fromKey}-${toKey}`,
        source: fromKey,
        target: toKey,
        animated: activeStage === toKey,
        style: { stroke: isLive ? '#3B82F6' : 'rgba(148,163,184,0.25)', strokeWidth: 1.5 },
      });
    }

    return { nodes, edges };
  }, [activeStage, completedStages]);

  return (
    <div className="h-[360px] rounded-card overflow-hidden border border-line glass">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
        nodesDraggable={false}
        nodesConnectable={false}
        zoomOnScroll={false}
        panOnDrag={true}
      >
        <Background color="rgba(148,163,184,0.15)" gap={24} />
      </ReactFlow>
    </div>
  );
}
