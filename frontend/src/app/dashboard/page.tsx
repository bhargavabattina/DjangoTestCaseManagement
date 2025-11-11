'use client';

import { useEffect, useState } from 'react';
import AuthLayout from '@/components/layout/AuthLayout';
import { dashboardAPI } from '@/lib/api';
import { DashboardStats } from '@/types';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await dashboardAPI.getStats();
      setStats(response.data);
    } catch (error) {
      toast.error('Failed to load dashboard stats');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <AuthLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0 animate-fade-in">
        <div className="page-header">
          <h1 className="page-title">Dashboard Overview</h1>
          <p className="text-gray-600 mt-2">Welcome back! Here's what's happening with your test management.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="stats-card from-blue-500 to-blue-600">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-blue-100 uppercase tracking-wide">Projects</h3>
                <p className="text-4xl font-extrabold text-white mt-3">{stats?.projects_count || 0}</p>
              </div>
              <div className="h-16 w-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          <div className="stats-card from-purple-500 to-purple-600">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-purple-100 uppercase tracking-wide">Epics</h3>
                <p className="text-4xl font-extrabold text-white mt-3">{stats?.epics_count || 0}</p>
              </div>
              <div className="h-16 w-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
          </div>
          <div className="stats-card from-indigo-500 to-indigo-600">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-indigo-100 uppercase tracking-wide">User Stories</h3>
                <p className="text-4xl font-extrabold text-white mt-3">{stats?.stories_count || 0}</p>
              </div>
              <div className="h-16 w-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          <div className="stats-card from-green-500 to-green-600">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-green-100 uppercase tracking-wide">Test Cases</h3>
                <p className="text-4xl font-extrabold text-white mt-3">{stats?.testcases_count || 0}</p>
              </div>
              <div className="h-16 w-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Execution Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card bg-gradient-to-br from-cyan-50 to-blue-50 border-l-4 border-cyan-500 hover:shadow-xl transition-all">
            <div className="flex items-center space-x-4">
              <div className="h-14 w-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-600 uppercase">Total Executions</h3>
                <p className="text-3xl font-bold text-cyan-700 mt-1">{stats?.total_executions || 0}</p>
              </div>
            </div>
          </div>
          <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-l-4 border-green-500 hover:shadow-xl transition-all">
            <div className="flex items-center space-x-4">
              <div className="h-14 w-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-600 uppercase">Passed Tests</h3>
                <p className="text-3xl font-bold text-green-700 mt-1">{stats?.passed_executions || 0}</p>
              </div>
            </div>
          </div>
          <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-l-4 border-purple-500 hover:shadow-xl transition-all">
            <div className="flex items-center space-x-4">
              <div className="h-14 w-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-600 uppercase">Pass Rate</h3>
                <p className="text-3xl font-bold text-purple-700 mt-1">{stats?.pass_rate || 0}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card hover:shadow-2xl transition-all">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Recent Projects</h2>
              <span className="badge badge-info">{stats?.recent_projects?.length || 0}</span>
            </div>
            <div className="space-y-4">
              {stats?.recent_projects?.map((project) => (
                <div key={project.id} className="border-l-4 border-primary-500 pl-4 py-2 bg-gradient-to-r from-primary-50 to-transparent rounded-r-lg hover:from-primary-100 transition-colors">
                  <p className="font-semibold text-gray-900">{project.name}</p>
                  <p className="text-sm text-gray-600 mt-1">{project.description?.substring(0, 60)}...</p>
                </div>
              ))}
              {(!stats?.recent_projects || stats.recent_projects.length === 0) && (
                <div className="text-center py-8">
                  <svg className="h-16 w-16 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  <p className="text-gray-500 text-sm">No recent projects</p>
                </div>
              )}
            </div>
          </div>

          <div className="card hover:shadow-2xl transition-all">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Recent Test Cases</h2>
              <span className="badge badge-success">{stats?.recent_testcases?.length || 0}</span>
            </div>
            <div className="space-y-4">
              {stats?.recent_testcases?.map((testcase: any) => (
                <div key={testcase.id} className="border-l-4 border-blue-500 pl-4 py-2 bg-gradient-to-r from-blue-50 to-transparent rounded-r-lg hover:from-blue-100 transition-colors">
                  <p className="font-semibold text-gray-900">{testcase.name}</p>
                  <p className="text-sm text-gray-600 mt-1">{testcase.project_name}</p>
                </div>
              ))}
              {(!stats?.recent_testcases || stats.recent_testcases.length === 0) && (
                <div className="text-center py-8">
                  <svg className="h-16 w-16 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <p className="text-gray-500 text-sm">No recent test cases</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
