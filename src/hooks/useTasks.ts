import { useEffect, useState } from 'react';
import { Task } from '../types/task';
import { getRecentTasks } from '../services/taskService';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRecentTasks().then((data) => {
      setTasks(data);
      setLoading(false);
    });
  }, []);

  return { tasks, loading };
}
