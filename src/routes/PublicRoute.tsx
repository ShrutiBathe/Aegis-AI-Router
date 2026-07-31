import { Outlet } from 'react-router-dom';

// Wraps routes that never require auth (landing, login, register).
export default function PublicRoute() {
  return <Outlet />;
}
