'use client';

import { useState, useEffect } from 'react';
import AuthLayout from '@/components/layout/AuthLayout';
import Modal from '@/components/ui/Modal';
import Table from '@/components/ui/Table';
import Loading from '@/components/ui/Loading';
import { testCasesAPI, projectsAPI, helpersAPI } from '@/lib/api';
import { TestCase, Project, Epic, UserStory } from '@/types';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon, TrashIcon, PlayIcon } from '@heroicons/react/24/outline';

export default function TestCasesPage() {
  const [testCases, setTestCases] = useState<any[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [epics, setEpics] = useState<any[]>([]);
  const [stories, setStories] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_steps: '',
    expected_results: '',
    status: 'draft' as any,
    execution_status: 'not_executed' as any,
    priority: 'medium' as any,
    is_automated: false,
    user_story: '',
    project: '',
    epic: '',
  });

  useEffect(() => {
    fetchProjects();
    fetchTestCases();
  }, [searchQuery]);

  useEffect(() => {
    if (formData.project) {
      fetchEpicsByProject(Number(formData.project));
    }
  }, [formData.project]);

  useEffect(() => {
    if (formData.epic) {
      fetchStoriesByEpic(Number(formData.epic));
    }
  }, [formData.epic]);

  const fetchProjects = async () => {
    try {
      const response = await projectsAPI.getAll();
      setProjects(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load projects');
    }
  };

  const fetchEpicsByProject = async (projectId: number) => {
    try {
      const response = await helpersAPI.getEpicsByProject(projectId);
      setEpics(response.data);
    } catch (error) {
      toast.error('Failed to load epics');
    }
  };

  const fetchStoriesByEpic = async (epicId: number) => {
    try {
      const response = await helpersAPI.getStoriesByEpic(epicId);
      setStories(response.data);
    } catch (error) {
      toast.error('Failed to load stories');
    }
  };

  const fetchTestCases = async () => {
    try {
      const response = await testCasesAPI.getAll({ search: searchQuery });
      setTestCases(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load test cases');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedTestCase) {
        await testCasesAPI.update(selectedTestCase.id, formData);
        toast.success('Test Case updated successfully!');
      } else {
        await testCasesAPI.create(formData);
        toast.success('Test Case created successfully!');
      }

      setShowModal(false);
      resetForm();
      fetchTestCases();
    } catch (error: any) {
      toast.error(error.response?.data?.name?.[0] || 'Operation failed');
    }
  };

  const handleExecute = async (executionStatus: string) => {
    if (!selectedTestCase) return;
    try {
      await testCasesAPI.execute(selectedTestCase.id, executionStatus);
      toast.success(`Test Case marked as ${executionStatus}!`);
      setShowExecuteModal(false);
      setSelectedTestCase(null);
      fetchTestCases();
    } catch (error) {
      toast.error('Failed to execute test case');
    }
  };

  const handleDelete = async () => {
    if (!selectedTestCase) return;
    try {
      await testCasesAPI.delete(selectedTestCase.id);
      toast.success('Test Case deleted successfully!');
      setShowDeleteModal(false);
      setSelectedTestCase(null);
      fetchTestCases();
    } catch (error) {
      toast.error('Failed to delete test case');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      test_steps: '',
      expected_results: '',
      status: 'draft',
      execution_status: 'not_executed',
      priority: 'medium',
      is_automated: false,
      user_story: '',
      project: '',
      epic: '',
    });
    setSelectedTestCase(null);
  };

  const openEditModal = (testCase: any) => {
    setSelectedTestCase(testCase);
    setFormData({
      name: testCase.name,
      description: testCase.description,
      test_steps: testCase.test_steps,
      expected_results: testCase.expected_results,
      status: testCase.status,
      execution_status: testCase.execution_status,
      priority: testCase.priority,
      is_automated: testCase.is_automated,
      user_story: testCase.user_story.toString(),
      project: '',
      epic: '',
    });
    setShowModal(true);
  };

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'user_story_name', label: 'User Story' },
    { key: 'project_name', label: 'Project' },
    {
      key: 'priority',
      label: 'Priority',
      render: (value: string) => (
        <span className={`badge ${
          value === 'critical' ? 'badge-danger' :
          value === 'high' ? 'badge-warning' :
          value === 'medium' ? 'badge-info' : 'badge-secondary'
        }`}>
          {value}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value: string) => (
        <span className={`badge ${
          value === 'ready' ? 'badge-success' :
          value === 'blocked' ? 'badge-danger' : 'badge-secondary'
        }`}>
          {value}
        </span>
      ),
    },
    {
      key: 'execution_status',
      label: 'Execution',
      render: (value: string) => (
        <span className={`badge ${
          value === 'passed' ? 'badge-success' :
          value === 'failed' ? 'badge-danger' :
          value === 'skipped' ? 'badge-warning' : 'badge-secondary'
        }`}>
          {value.replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'is_automated',
      label: 'Type',
      render: (value: boolean) => (
        <span className={`badge ${value ? 'badge-info' : 'badge-secondary'}`}>
          {value ? 'Automated' : 'Manual'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_: any, row: any) => (
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedTestCase(row);
              setShowExecuteModal(true);
            }}
            className="text-green-600 hover:text-green-900"
            title="Execute"
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
              setSelectedTestCase(row);
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
        <Loading text="Loading test cases..." />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0 animate-fade-in">
        <div className="page-header">
          <div className="sm:flex sm:items-center sm:justify-between">
            <div>
              <h1 className="page-title">Test Cases</h1>
              <p className="text-gray-600 mt-2">Create and manage your test case library</p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary mt-4 sm:mt-0 flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Test Case
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <input
              type="text"
              placeholder="Search test cases..."
              className="input pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <svg className="h-5 w-5 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Test Cases Table */}
        <div className="card hover:shadow-2xl transition-all">
          <Table columns={columns} data={testCases} />
        </div>

        {/* Create/Edit Modal */}
        <Modal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            resetForm();
          }}
          title={selectedTestCase ? 'Edit Test Case' : 'Create Test Case'}
          size="xl"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Project *</label>
                <select
                  className="input"
                  value={formData.project}
                  onChange={(e) => setFormData({ ...formData, project: e.target.value, epic: '', user_story: '' })}
                  required
                >
                  <option value="">Select Project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Epic *</label>
                <select
                  className="input"
                  value={formData.epic}
                  onChange={(e) => setFormData({ ...formData, epic: e.target.value, user_story: '' })}
                  required
                  disabled={!formData.project}
                >
                  <option value="">Select Epic</option>
                  {epics.map((epic) => (
                    <option key={epic.id} value={epic.id}>
                      {epic.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">User Story *</label>
                <select
                  className="input"
                  value={formData.user_story}
                  onChange={(e) => setFormData({ ...formData, user_story: e.target.value })}
                  required
                  disabled={!formData.epic}
                >
                  <option value="">Select User Story</option>
                  {stories.map((story) => (
                    <option key={story.id} value={story.id}>
                      {story.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

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
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div>
              <label className="label">Test Steps *</label>
              <textarea
                className="input"
                rows={4}
                value={formData.test_steps}
                onChange={(e) => setFormData({ ...formData, test_steps: e.target.value })}
                required
                placeholder="1. Step one&#10;2. Step two&#10;3. Step three"
              />
            </div>

            <div>
              <label className="label">Expected Results *</label>
              <textarea
                className="input"
                rows={3}
                value={formData.expected_results}
                onChange={(e) => setFormData({ ...formData, expected_results: e.target.value })}
                required
              />
            </div>

            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="label">Status</label>
                <select
                  className="input"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="draft">Draft</option>
                  <option value="ready">Ready</option>
                  <option value="blocked">Blocked</option>
                </select>
              </div>
              <div>
                <label className="label">Priority</label>
                <select
                  className="input"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label className="label">Execution Status</label>
                <select
                  className="input"
                  value={formData.execution_status}
                  onChange={(e) => setFormData({ ...formData, execution_status: e.target.value })}
                >
                  <option value="not_executed">Not Executed</option>
                  <option value="passed">Passed</option>
                  <option value="failed">Failed</option>
                  <option value="skipped">Skipped</option>
                </select>
              </div>
              <div>
                <label className="label">Automated</label>
                <div className="flex items-center h-10">
                  <input
                    type="checkbox"
                    className="h-5 w-5 text-primary-600 rounded"
                    checked={formData.is_automated}
                    onChange={(e) => setFormData({ ...formData, is_automated: e.target.checked })}
                  />
                  <span className="ml-2 text-sm text-gray-700">Automated Test</span>
                </div>
              </div>
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
                {selectedTestCase ? 'Update' : 'Create'} Test Case
              </button>
            </div>
          </form>
        </Modal>

        {/* Execute Modal */}
        <Modal
          isOpen={showExecuteModal}
          onClose={() => {
            setShowExecuteModal(false);
            setSelectedTestCase(null);
          }}
          title="Execute Test Case"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">
              <strong>{selectedTestCase?.name}</strong>
            </p>
            <div className="space-y-2">
              <button
                onClick={() => handleExecute('passed')}
                className="w-full btn bg-green-600 text-white hover:bg-green-700"
              >
                Mark as Passed
              </button>
              <button
                onClick={() => handleExecute('failed')}
                className="w-full btn bg-red-600 text-white hover:bg-red-700"
              >
                Mark as Failed
              </button>
              <button
                onClick={() => handleExecute('skipped')}
                className="w-full btn bg-yellow-600 text-white hover:bg-yellow-700"
              >
                Mark as Skipped
              </button>
            </div>
            <button
              onClick={() => setShowExecuteModal(false)}
              className="w-full btn-secondary mt-4"
            >
              Cancel
            </button>
          </div>
        </Modal>

        {/* Delete Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedTestCase(null);
          }}
          title="Delete Test Case"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{selectedTestCase?.name}</strong>?
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
