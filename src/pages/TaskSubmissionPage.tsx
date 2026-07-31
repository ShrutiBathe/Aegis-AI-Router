import TaskForm from '../components/tasks/TaskForm';
import PipelineFlow from '../components/router/PipelineFlow';

export default function TaskSubmissionPage() {
  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-8">
      <div className="text-center">
        <h1 className="font-display text-2xl text-ink mb-2">Submit a Task</h1>
        <p className="text-sm text-ink-muted">Your request enters the pipeline the moment you route it.</p>
      </div>
      <TaskForm />
      <div className="glass rounded-card p-6">
        <PipelineFlow mode="idle" />
      </div>
    </div>
  );
}
