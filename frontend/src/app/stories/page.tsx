'use client';

import { useState, useEffect } from 'react';
import AuthLayout from '@/components/layout/AuthLayout';
import Modal from '@/components/ui/Modal';
import Table from '@/components/ui/Table';
import Loading from '@/components/ui/Loading';
import { storiesAPI, projectsAPI, epicsAPI, helpersAPI } from '@/lib/api';
import { UserStory, Project, Epic } from '@/types';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function StoriesPage() {
  const [stories, setStories] = useState<UserStory[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [epics, setEpics] = useState<Epic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedStory, setSelectedStory] = useState<UserStory | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    acceptance_criteria: '',
    status: 'todo' as any,
    priority: 'medium' as any,
    story_points: '',
    epic: '',
    project: '',
  });

  useEffect(() => {
    fetchProjects();
    fetchStories();
  }, [searchQuery]);

  useEffect(() => {
    if (formData.project) {
      fetchEpicsByProject(Number(formData.project));
    }
  }, [formData.project]);

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

  const fetchStories = async () => {
    try {
      const response = await storiesAPI.getAll({ search: searchQuery });
      setStories(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load user stories');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        story_points: formData.story_points ? Number(formData.story_points) : null,
      };

      if (selectedStory) {
        await storiesAPI.update(selectedStory.id, data);
        toast.success('User Story updated successfully!');
      } else {
        await storiesAPI.create(data);
        toast.success('User Story created successfully!');
      }

      setShowModal(false);
      resetForm();
      fetchStories();
    } catch (error: any) {
      toast.error(error.response?.data?.name?.[0] || 'Operation failed');
    }
  };

  const handleDelete = async () => {
    if (!selectedStory) return;
    try {
      await storiesAPI.delete(selectedStory.id);
      toast.success('User Story deleted successfully!');
      setShowDeleteModal(false);
      setSelectedStory(null);
      fetchStories();
    } catch (error) {
      toast.error('Failed to delete user story');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      acceptance_criteria: '',
      status: 'todo',
      priority: 'medium',
      story_points: '',
      epic: '',
      project: '',
    });
    setSelectedStory(null);
  };

  const openEditModal = (story: UserStory) => {
    setSelectedStory(story);
    setFormData({
      name: story.name,
      description: story.description,
      acceptance_criteria: story.acceptance_criteria,
      status: story.status,
      priority: story.priority,
      story_points: story.story_points?.toString() || '',
      epic: story.epic.toString(),
      project: '', // Will be set when epics load
    });
    setShowModal(true);
  };

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'epic_name', label: 'Epic' },
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
          value === 'done' ? 'badge-success' :
          value === 'testing' ? 'badge-warning' :
          value === 'in_progress' ? 'badge-info' : 'badge-secondary'
        }`}>
          {value.replace('_', ' ')}
        </span>
      ),
    },
    { key: 'story_points', label: 'Points' },
    { key: 'testcases_count', label: 'Test Cases' },
    {
      key: 'actions',
      label: 'Actions',
      render: (_: any, row: UserStory) => (
        <div className="flex space-x-2">
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
              setSelectedStory(row);
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
        <Loading text="Loading user stories..." />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0">
        <div className="sm:flex sm:items-center sm:justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">User Stories</h1>
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary mt-4 sm:mt-0 flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New User Story
          </button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search user stories..."
            className="input max-w-md"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Stories Table */}
        <div className="card">
          <Table columns={columns} data={stories} />
        </div>

        {/* Create/Edit Modal */}
        <Modal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            resetForm();
          }}
          title={selectedStory ? 'Edit User Story' : 'Create User Story'}
          size="lg"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Project *</label>
                <select
                  className="input"
                  value={formData.project}
                  onChange={(e) => setFormData({ ...formData, project: e.target.value, epic: '' })}
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
                  onChange={(e) => setFormData({ ...formData, epic: e.target.value })}
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
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Acceptance Criteria</label>
              <textarea
                className="input"
                rows={3}
                value={formData.acceptance_criteria}
                onChange={(e) => setFormData({ ...formData, acceptance_criteria: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Status</label>
                <select
                  className="input"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="testing">Testing</option>
                  <option value="done">Done</option>
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
                <label className="label">Story Points</label>
                <input
                  type="number"
                  className="input"
                  min="1"
                  value={formData.story_points}
                  onChange={(e) => setFormData({ ...formData, story_points: e.target.value })}
                />
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
                {selectedStory ? 'Update' : 'Create'} User Story
              </button>
            </div>
          </form>
        </Modal>

        {/* Delete Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedStory(null);
          }}
          title="Delete User Story"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{selectedStory?.name}</strong>?
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
