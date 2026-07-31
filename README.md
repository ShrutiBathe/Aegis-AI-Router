# Aegis Router — Frontend

The Operating System for AI Agents. React + TypeScript + Vite frontend implementing
the full flow: Discover → Route → Pay → Execute → Monitor.

## Stack
- React 18 + TypeScript + Vite
- Tailwind CSS (dark glassmorphism theme, blue/purple gradients)
- React Router for navigation
- React Flow for the live pipeline visualization
- Recharts for analytics
- Framer Motion for animation

## Structure
See `src/` — organized into `components/` (by feature domain), `pages/`,
`services/` (currently mocked, swap in real API calls), `hooks/`, `contexts/`,
`routes/`, `types/`, `utils/`, `styles/`.

## Design signature
`PipelineFlow` (`src/components/router/PipelineFlow.tsx`) is the one component
reused across the app — landing hero, navbar mini-strip, dashboard health,
and the live Router Execution page — so the orchestration story (User → Router
→ Planner → Registry → Ranking → Payment → Execution → Results) stays visible
everywhere, not just on one "demo" screen.

## Run locally
```
npm install
npm run dev
```

## Auth (demo)
Login/Register accept any email/password — this is a mocked auth service in
`src/services/authService.ts` for demo purposes. Swap in real endpoints when
the backend is ready.
