'use client';

import { useState, useEffect } from 'react';
import AuthLayout from '@/components/layout/AuthLayout';
import Modal from '@/components/ui/Modal';
import Table from '@/components/ui/Table';
import Loading from '@/components/ui/Loading';
import { epicsAPI, projectsAPI } from '@/lib/api';
import { Epic, Project } from '@/types';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function EpicsPage() {
  const [epics, setEpics] = useState<Epic[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState<number | ''>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedEpic, setSelectedEpic] = useState<Epic | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'open' as 'open' | 'in_progress' | 'closed',
    project: '',
  });

  useEffect(() => {
    fetchProjects();
    fetchEpics();
  }, [searchQuery, selectedProject]);

  const fetchProjects = async () => {
    try {
      const response = await projectsAPI.getAll();
      setProjects(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load projects');
    }
  };

  const fetchEpics = async () => {
    try {
      const params: any = { search: searchQuery };
      if (selectedProject) params.project = selectedProject;
      const response = await epicsAPI.getAll(params);
      setEpics(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load epics');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await epicsAPI.create(formData);
      toast.success('Epic created successfully!');
      setShowCreateModal(false);
      setFormData({ name: '', description: '', status: 'open', project: '' });
      fetchEpics();
    } catch (error: any) {
      toast.error(error.response?.data?.name?.[0] || 'Failed to create epic');
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEpic) return;
    try {
      await epicsAPI.update(selectedEpic.id, formData);
      toast.success('Epic updated successfully!');
      setShowEditModal(false);
      setSelectedEpic(null);
      fetchEpics();
    } catch (error) {
      toast.error('Failed to update epic');
    }
  };

  const handleDelete = async () => {
    if (!selectedEpic) return;
    try {
      await epicsAPI.delete(selectedEpic.id);
      toast.success('Epic deleted successfully!');
      setShowDeleteModal(false);
      setSelectedEpic(null);
      fetchEpics();
    } catch (error) {
      toast.error('Failed to delete epic');
    }
  };

  const openEditModal = (epic: Epic) => {
    setSelectedEpic(epic);
    setFormData({
      name: epic.name,
      description: epic.description,
      status: epic.status,
      project: epic.project.toString(),
    });
    setShowEditModal(true);
  };

  const openDeleteModal = (epic: Epic) => {
    setSelectedEpic(epic);
    setShowDeleteModal(true);
  };

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'project_name', label: 'Project' },
    { key: 'description', label: 'Description' },
    {
      key: 'status',
      label: 'Status',
      render: (value: string) => (
        <span className={`badge ${
          value === 'open' ? 'badge-info' :
          value === 'in_progress' ? 'badge-warning' : 'badge-success'
        }`}>
          {value.replace('_', ' ')}
        </span>
      ),
    },
    { key: 'stories_count', label: 'Stories' },
    {
      key: 'actions',
      label: 'Actions',
      render: (_: any, row: Epic) => (
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
              openDeleteModal(row);
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
        <Loading text="Loading epics..." />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="px-4 sm:px-0 animate-fade-in">
        <div className="page-header">
          <div className="sm:flex sm:items-center sm:justify-between">
            <div>
              <h1 className="page-title">Epics</h1>
              <p className="text-gray-600 mt-2">Organize your work into manageable epics</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary mt-4 sm:mt-0 flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Epic
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search epics..."
              className="input pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <svg className="h-5 w-5 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div className="relative">
            <select
              className="input pl-10"
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : '')}
            >
              <option value="">All Projects</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
            <svg className="h-5 w-5 text-gray-400 absolute left-3 top-3 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </div>
        </div>

        {/* Epics Table */}
        <div className="card hover:shadow-2xl transition-all">
          <Table columns={columns} data={epics} />
        </div>

        {/* Create/Edit Modal */}
        <Modal
          isOpen={showCreateModal || showEditModal}
          onClose={() => {
            setShowCreateModal(false);
            setShowEditModal(false);
            setSelectedEpic(null);
            setFormData({ name: '', description: '', status: 'open', project: '' });
          }}
          title={showCreateModal ? 'Create Epic' : 'Edit Epic'}
        >
          <form onSubmit={showCreateModal ? handleCreate : handleEdit} className="space-y-4">
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
              <label className="label">Project *</label>
              <select
                className="input"
                value={formData.project}
                onChange={(e) => setFormData({ ...formData, project: e.target.value })}
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
              <label className="label">Description</label>
              <textarea
                className="input"
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Status</label>
              <select
                className="input"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
              >
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowCreateModal(false);
                  setShowEditModal(false);
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {showCreateModal ? 'Create' : 'Update'} Epic
              </button>
            </div>
          </form>
        </Modal>

        {/* Delete Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedEpic(null);
          }}
          title="Delete Epic"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{selectedEpic?.name}</strong>?
              This will also delete all associated user stories.
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
