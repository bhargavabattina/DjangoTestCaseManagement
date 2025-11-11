'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AuthLayout from '@/components/layout/AuthLayout';
import Modal from '@/components/ui/Modal';
import Table from '@/components/ui/Table';
import Loading from '@/components/ui/Loading';
import { testRunsAPI, testCasesAPI, testExecutionsAPI } from '@/lib/api';
import { TestRun } from '@/types';
import toast from 'react-hot-toast';
import { PlusIcon, PlayIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';

export default function TestRunsPage() {
  const router = useRouter();
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [testCases, setTestCases] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [selectedRun, setSelectedRun] = useState<TestRun | null>(null);
  const [executions, setExecutions] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'not_started' as any,
    test_case_ids: [] as number[],
  });

  useEffect(() => {
    fetchTestCases();
    fetchTestRuns();
  }, [searchQuery]);

  const fetchTestCases = async () => {
    try {
      const response = await testCasesAPI.getAll();
      setTestCases(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load test cases');
    }
  };

  const fetchTestRuns = async () => {
    try {
      const response = await testRunsAPI.getAll({ search: searchQuery });
      setTestRuns(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load test runs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await testRunsAPI.create(formData);
      toast.success('Test Run created successfully!');
      setShowCreateModal(false);
      setFormData({ name: '', description: '', status: 'not_started', test_case_ids: [] });
      fetchTestRuns();
    } catch (error: any) {
      toast.error(error.response?.data?.name?.[0] || 'Failed to create test run');
    }
  };

  const handleDelete = async () => {
    if (!selectedRun) return;
    try {
      await testRunsAPI.delete(selectedRun.id);
      toast.success('Test Run deleted successfully!');
      setShowDeleteModal(false);
      setSelectedRun(null);
      fetchTestRuns();
    } catch (error) {
      toast.error('Failed to delete test run');
    }
  };

  const openExecuteModal = async (run: TestRun) => {
    setSelectedRun(run);
    try {
      const response = await testRunsAPI.getExecutions(run.id);
      setExecutions(response.data);
      setShowExecuteModal(true);
    } catch (error) {
      toast.error('Failed to load test executions');
    }
  };

  const handleExecuteTest = async (executionId: number, status: string) => {
    try {
      await testExecutionsAPI.recordResult(executionId, { status });
      toast.success(`Test marked as ${status}!`);
      if (selectedRun) {
        const response = await testRunsAPI.getExecutions(selectedRun.id);
        setExecutions(response.data);
      }
    } catch (error) {
      toast.error('Failed to update test execution');
    }
  };

  const toggleTestCase = (testCaseId: number) => {
    setFormData((prev) => ({
      ...prev,
      test_case_ids: prev.test_case_ids.includes(testCaseId)
        ? prev.test_case_ids.filter((id) => id !== testCaseId)
        : [...prev.test_case_ids, testCaseId],
    }));
  };

  const columns = [
    { key: 'name', label: 'Name' },
    {
      key: 'status',
      label: 'Status',
      render: (value: string) => (
        <span className={`badge ${
          value === 'completed' ? 'badge-success' :
          value === 'in_progress' ? 'badge-warning' :
          value === 'cancelled' ? 'badge-danger' : 'badge-secondary'
        }`}>
          {value.replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'execution_summary',
      label: 'Progress',
      render: (summary: any) => (
        <div className="text-sm">
          <span className="text-green-600">{summary.passed}</span> /
          <span className="text-red-600"> {summary.failed}</span> /
          <span className="text-gray-600"> {summary.total}</span>
        </div>
      ),
    },
    {
      key: 'execution_summary',
      label: 'Pass Rate',
      render: (summary: any) => (
        <span className="text-sm font-medium">{summary.passed_percentage}%</span>
      ),
    },
    {
      key: 'created_date',
      label: 'Created',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_: any, row: TestRun) => (
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              openExecuteModal(row);
            }}
            className="text-green-600 hover:text-green-900"
            title="Execute"
          >
            <PlayIcon className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedRun(row);
              setShowDeleteModal(true);
            }}
            className="text-red-600 hover:text-red-900"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      ),
    },
  ];

  if (isLoading) {
    return (
      <AuthLayout>
        <Loading text="Loading test runs..." />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0">
        <div className="sm:flex sm:items-center sm:justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Test Runs</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary mt-4 sm:mt-0 flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Test Run
          </button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search test runs..."
            className="input max-w-md"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Test Runs Table */}
        <div className="card">
          <Table columns={columns} data={testRuns} />
        </div>

        {/* Create Modal */}
        <Modal
          isOpen={showCreateModal}
          onClose={() => {
            setShowCreateModal(false);
            setFormData({ name: '', description: '', status: 'not_started', test_case_ids: [] });
          }}
          title="Create Test Run"
          size="lg"
        >
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="label">Name *</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="label">Description</label>
              <textarea
                className="input"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div>
              <label className="label">Select Test Cases *</label>
              <div className="border border-gray-300 rounded-md p-4 max-h-64 overflow-y-auto">
                {testCases.length === 0 ? (
                  <p className="text-gray-500 text-sm">No test cases available</p>
                ) : (
                  testCases.map((testCase) => (
                    <label key={testCase.id} className="flex items-center py-2 hover:bg-gray-50 px-2 rounded">
                      <input
                        type="checkbox"
                        className="h-4 w-4 text-primary-600 rounded"
                        checked={formData.test_case_ids.includes(testCase.id)}
                        onChange={() => toggleTestCase(testCase.id)}
                      />
                      <span className="ml-3 text-sm text-gray-900">{testCase.name}</span>
                      <span className="ml-auto text-xs text-gray-500">{testCase.project_name}</span>
                    </label>
                  ))
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {formData.test_case_ids.length} test case(s) selected
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Create Test Run
              </button>
            </div>
          </form>
        </Modal>

        {/* Execute Modal */}
        <Modal
          isOpen={showExecuteModal}
          onClose={() => {
            setShowExecuteModal(false);
            setSelectedRun(null);
            setExecutions([]);
          }}
          title={`Execute: ${selectedRun?.name}`}
          size="xl"
        >
          <div className="space-y-4">
            {/* Summary */}
            {selectedRun && (
              <div className="grid grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold">{selectedRun.execution_summary.total}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Passed</p>
                  <p className="text-2xl font-bold text-green-600">{selectedRun.execution_summary.passed}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Failed</p>
                  <p className="text-2xl font-bold text-red-600">{selectedRun.execution_summary.failed}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Pass Rate</p>
                  <p className="text-2xl font-bold text-primary-600">{selectedRun.execution_summary.passed_percentage}%</p>
                </div>
              </div>
            )}

            {/* Executions List */}
            <div className="max-h-96 overflow-y-auto">
              {executions.map((execution) => (
                <div key={execution.id} className="border-b border-gray-200 py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{execution.testcase.name}</h4>
                      <p className="text-sm text-gray-500 mt-1">
                        {execution.testcase.project_name} &gt; {execution.testcase.user_story_name}
                      </p>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleExecuteTest(execution.id, 'passed')}
                        className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                      >
                        Pass
                      </button>
                      <button
                        onClick={() => handleExecuteTest(execution.id, 'failed')}
                        className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                      >
                        Fail
                      </button>
                      <button
                        onClick={() => handleExecuteTest(execution.id, 'skipped')}
                        className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                      >
                        Skip
                      </button>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span className={`badge ${
                      execution.status === 'passed' ? 'badge-success' :
                      execution.status === 'failed' ? 'badge-danger' :
                      execution.status === 'skipped' ? 'badge-warning' : 'badge-secondary'
                    }`}>
                      {execution.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => {
                  setShowExecuteModal(false);
                  fetchTestRuns();
                }}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          </div>
        </Modal>

        {/* Delete Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedRun(null);
          }}
          title="Delete Test Run"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{selectedRun?.name}</strong>?
            </p>
            <div className="flex justify-end space-x-3">
              <button onClick={() => setShowDeleteModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={handleDelete} className="btn-danger">
                Delete
              </button>
            </div>
          </div>
        </Modal>
      </div>
    </AuthLayout>
  );
}
