'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import {
  HomeIcon,
  FolderIcon,
  DocumentTextIcon,
  BookOpenIcon,
  ClipboardDocumentCheckIcon,
  RectangleStackIcon,
  PlayIcon,
  ArrowRightOnRectangleIcon,
  BeakerIcon,
} from '@heroicons/react/24/outline';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/');

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
    { path: '/projects', label: 'Projects', icon: FolderIcon },
    { path: '/epics', label: 'Epics', icon: BookOpenIcon },
    { path: '/stories', label: 'Stories', icon: DocumentTextIcon },
    { path: '/testcases', label: 'Test Cases', icon: ClipboardDocumentCheckIcon },
    { path: '/test-suites', label: 'Test Suites', icon: RectangleStackIcon },
    { path: '/test-runs', label: 'Test Runs', icon: PlayIcon },
  ];

  return (
    <nav className="bg-gradient-to-r from-primary-600 via-primary-700 to-indigo-700 shadow-2xl sticky top-0 z-50 animate-slide-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/dashboard" className="flex items-center space-x-2 group">
                <BeakerIcon className="h-8 w-8 text-white group-hover:scale-110 transition-transform duration-200" />
                <span className="text-xl font-extrabold text-white group-hover:text-blue-100 transition-colors">
                  TestHub
                </span>
              </Link>
            </div>
            <div className="hidden lg:ml-8 lg:flex lg:space-x-1">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Link
                  key={path}
                  href={path}
                  className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    isActive(path)
                      ? 'bg-white text-primary-700 shadow-lg scale-105'
                      : 'text-white hover:bg-white/20 hover:scale-105'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-3 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {(user?.full_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
              </div>
              <span className="text-white font-medium">{user?.full_name || user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white font-semibold rounded-lg transition-all duration-200 hover:scale-105 shadow-lg"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
