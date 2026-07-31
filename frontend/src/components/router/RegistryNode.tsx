import { Handle, Position } from 'reactflow';

// RegistryNode is available for future custom React Flow node rendering
// (icons/metadata per stage). WorkflowGraph currently renders stages with
// shared styling; swap in these per-stage nodes via nodeTypes when richer
// per-node content (icons, live metrics) is needed.
export default function RegistryNode({ data }: { data: { label: string } }) {
  return (
    <div className="px-4 py-2 rounded-card border border-line glass text-xs text-ink">
      <Handle type="target" position={Position.Left} />
      {data.label}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
