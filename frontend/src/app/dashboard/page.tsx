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
      <div className="px-4 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Projects</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{stats?.projects_count || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Epics</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{stats?.epics_count || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">User Stories</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{stats?.stories_count || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Test Cases</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{stats?.testcases_count || 0}</p>
          </div>
        </div>

        {/* Execution Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Total Executions</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">{stats?.total_executions || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Passed Tests</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">{stats?.passed_executions || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Pass Rate</h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">{stats?.pass_rate || 0}%</p>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Projects</h2>
            <div className="space-y-3">
              {stats?.recent_projects.map((project) => (
                <div key={project.id} className="border-l-4 border-primary-500 pl-3">
                  <p className="font-medium text-gray-900">{project.name}</p>
                  <p className="text-sm text-gray-500">{project.description?.substring(0, 50)}...</p>
                </div>
              ))}
              {(!stats?.recent_projects || stats.recent_projects.length === 0) && (
                <p className="text-gray-500 text-sm">No recent projects</p>
              )}
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Test Cases</h2>
            <div className="space-y-3">
              {stats?.recent_testcases.map((testcase: any) => (
                <div key={testcase.id} className="border-l-4 border-blue-500 pl-3">
                  <p className="font-medium text-gray-900">{testcase.name}</p>
                  <p className="text-sm text-gray-500">{testcase.project_name}</p>
                </div>
              ))}
              {(!stats?.recent_testcases || stats.recent_testcases.length === 0) && (
                <p className="text-gray-500 text-sm">No recent test cases</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
