import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PromptEditor from './PromptEditor';
import BudgetSlider from './BudgetSlider';
import PrioritySelector from './PrioritySelector';
import LocalAIToggle from './LocalAIToggle';

export default function TaskForm() {
  const [prompt, setPrompt] = useState('');
  const [budget, setBudget] = useState(20);
  const [priority, setPriority] = useState('High Quality');
  const [localAI, setLocalAI] = useState(false);
  const navigate = useNavigate();

  function handleSubmit() {
    if (!prompt.trim()) return;
    navigate('/execute', { state: { prompt, budget, priority, localAI } });
  }

  return (
    <div className="glass rounded-card p-6 flex flex-col gap-5 max-w-2xl">
      <div>
        <h2 className="font-display text-lg text-ink mb-2">What would you like AI to do?</h2>
        <PromptEditor value={prompt} onChange={setPrompt} />
      </div>
      <BudgetSlider value={budget} onChange={setBudget} />
      <PrioritySelector value={priority} onChange={setPriority} />
      <LocalAIToggle checked={localAI} onChange={setLocalAI} />
      <button
        onClick={handleSubmit}
        disabled={!prompt.trim()}
        className="w-full py-3 rounded-chip bg-grad-primary text-white font-medium disabled:opacity-40 hover:opacity-90 transition"
      >
        Route Task
      </button>
    </div>
  );
}
