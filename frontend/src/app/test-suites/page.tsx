'use client';

import { useState, useEffect } from 'react';
import AuthLayout from '@/components/layout/AuthLayout';
import Modal from '@/components/ui/Modal';
import Table from '@/components/ui/Table';
import Loading from '@/components/ui/Loading';
import { testSuitesAPI, testCasesAPI } from '@/lib/api';
import { TestSuite } from '@/types';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon, TrashIcon, PlayIcon } from '@heroicons/react/24/outline';

export default function TestSuitesPage() {
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [testCases, setTestCases] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);
  const [selectedSuite, setSelectedSuite] = useState<TestSuite | null>(null);
  const [runName, setRunName] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_case_ids: [] as number[],
  });

  useEffect(() => {
    fetchTestCases();
    fetchTestSuites();
  }, [searchQuery]);

  const fetchTestCases = async () => {
    try {
      const response = await testCasesAPI.getAll();
      setTestCases(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load test cases');
    }
  };

  const fetchTestSuites = async () => {
    try {
      const response = await testSuitesAPI.getAll({ search: searchQuery });
      setTestSuites(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load test suites');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedSuite) {
        await testSuitesAPI.update(selectedSuite.id, formData);
        toast.success('Test Suite updated successfully!');
      } else {
        await testSuitesAPI.create(formData);
        toast.success('Test Suite created successfully!');
      }

      setShowModal(false);
      resetForm();
      fetchTestSuites();
    } catch (error: any) {
      toast.error(error.response?.data?.name?.[0] || 'Operation failed');
    }
  };

  const handleCreateRun = async () => {
    if (!selectedSuite || !runName) return;
    try {
      await testSuitesAPI.createTestRun(selectedSuite.id, { name: runName });
      toast.success('Test Run created successfully!');
      setShowRunModal(false);
      setSelectedSuite(null);
      setRunName('');
    } catch (error) {
      toast.error('Failed to create test run');
    }
  };

  const handleDelete = async () => {
    if (!selectedSuite) return;
    try {
      await testSuitesAPI.delete(selectedSuite.id);
      toast.success('Test Suite deleted successfully!');
      setShowDeleteModal(false);
      setSelectedSuite(null);
      fetchTestSuites();
    } catch (error) {
      toast.error('Failed to delete test suite');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      test_case_ids: [],
    });
    setSelectedSuite(null);
  };

  const openEditModal = (suite: TestSuite) => {
    setSelectedSuite(suite);
    setFormData({
      name: suite.name,
      description: suite.description,
      test_case_ids: suite.test_cases.map((tc) => tc.id),
    });
    setShowModal(true);
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
    { key: 'description', label: 'Description' },
    {
      key: 'statistics',
      label: 'Test Cases',
      render: (stats: any) => (
        <span className="text-gray-900">{stats?.total || 0}</span>
      ),
    },
    {
      key: 'statistics',
      label: 'Automated',
      render: (stats: any) => (
        <span className="badge badge-info">{stats?.automated || 0}</span>
      ),
    },
    {
      key: 'statistics',
      label: 'Ready',
      render: (stats: any) => (
        <span className="badge badge-success">{stats?.ready || 0}</span>
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
      render: (_: any, row: TestSuite) => (
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedSuite(row);
              setShowRunModal(true);
            }}
            className="text-green-600 hover:text-green-900"
            title="Create Test Run"
          >
            <PlayIcon className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              openEditModal(row);
            }}
            className="text-primary-600 hover:text-primary-900"
          >
            <PencilIcon className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedSuite(row);
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
        <Loading text="Loading test suites..." />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0 animate-fade-in">
        <div className="page-header">
          <div className="sm:flex sm:items-center sm:justify-between">
            <div>
              <h1 className="page-title">Test Suites</h1>
              <p className="text-gray-600 mt-2">Group test cases into organized suites</p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary mt-4 sm:mt-0 flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Test Suite
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <input
              type="text"
              placeholder="Search test suites..."
              className="input pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <svg className="h-5 w-5 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Test Suites Table */}
        <div className="card hover:shadow-2xl transition-all">
          <Table columns={columns} data={testSuites} />
        </div>

        {/* Create/Edit Modal */}
        <Modal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            resetForm();
          }}
          title={selectedSuite ? 'Edit Test Suite' : 'Create Test Suite'}
          size="lg"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
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
                onClick={() => {
                  setShowModal(false);
                  resetForm();
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {selectedSuite ? 'Update' : 'Create'} Test Suite
              </button>
            </div>
          </form>
        </Modal>

        {/* Create Test Run Modal */}
        <Modal
          isOpen={showRunModal}
          onClose={() => {
            setShowRunModal(false);
            setSelectedSuite(null);
            setRunName('');
          }}
          title="Create Test Run"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Create a test run from <strong>{selectedSuite?.name}</strong>
            </p>
            <div>
              <label className="label">Test Run Name *</label>
              <input
                type="text"
                className="input"
                value={runName}
                onChange={(e) => setRunName(e.target.value)}
                placeholder="e.g., Sprint 1 Regression"
                required
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRunModal(false);
                  setSelectedSuite(null);
                  setRunName('');
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button onClick={handleCreateRun} className="btn-primary">
                Create Test Run
              </button>
            </div>
          </div>
        </Modal>

        {/* Delete Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedSuite(null);
          }}
          title="Delete Test Suite"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{selectedSuite?.name}</strong>?
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
