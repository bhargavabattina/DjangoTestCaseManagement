'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/auth';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/');

  const navLinkClass = (path: string) =>
    `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
      isActive(path)
        ? 'border-primary-500 text-gray-900'
        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
    }`;

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-primary-600">
                Test Case Management
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link href="/dashboard" className={navLinkClass('/dashboard')}>
                Dashboard
              </Link>
              <Link href="/projects" className={navLinkClass('/projects')}>
                Projects
              </Link>
              <Link href="/epics" className={navLinkClass('/epics')}>
                Epics
              </Link>
              <Link href="/stories" className={navLinkClass('/stories')}>
                Stories
              </Link>
              <Link href="/testcases" className={navLinkClass('/testcases')}>
                Test Cases
              </Link>
              <Link href="/test-suites" className={navLinkClass('/test-suites')}>
                Test Suites
              </Link>
              <Link href="/test-runs" className={navLinkClass('/test-runs')}>
                Test Runs
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <span className="text-gray-700 mr-4">{user?.full_name || user?.username}</span>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
