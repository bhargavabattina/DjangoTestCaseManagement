export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'completed';
  created_by: User;
  created_date: string;
  updated_date: string;
  epics_count: number;
}

export interface Epic {
  id: number;
  name: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  project: number;
  project_name: string;
  created_by: User;
  created_date: string;
  updated_date: string;
  stories_count: number;
}

export interface UserStory {
  id: number;
  name: string;
  description: string;
  acceptance_criteria: string;
  status: 'todo' | 'in_progress' | 'testing' | 'done';
  priority: 'low' | 'medium' | 'high' | 'critical';
  story_points?: number;
  epic: number;
  epic_name: string;
  project_name: string;
  created_by: User;
  assigned_to?: User;
  assigned_to_id?: number;
  created_date: string;
  updated_date: string;
  testcases_count: number;
}

export interface TestCase {
  id: number;
  name: string;
  description: string;
  test_steps: string;
  expected_results: string;
  status: 'draft' | 'ready' | 'blocked';
  execution_status: 'not_executed' | 'passed' | 'failed' | 'skipped';
  priority: 'low' | 'medium' | 'high' | 'critical';
  is_automated: boolean;
  user_story: number;
  user_story_name: string;
  epic_name: string;
  project_name: string;
  created_by: User;
  assigned_to?: User;
  assigned_to_id?: number;
  created_date: string;
  updated_date: string;
  last_executed?: string;
}

export interface TestSuite {
  id: number;
  name: string;
  description: string;
  test_cases: TestCase[];
  test_case_ids?: number[];
  created_by: User;
  created_date: string;
  statistics: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    automated: number;
    manual: number;
    ready: number;
    draft: number;
    blocked: number;
  };
}

export interface TestExecution {
  id: number;
  testcase: TestCase;
  testcase_id?: number;
  test_run: number;
  executor?: User;
  status: 'not_executed' | 'in_progress' | 'passed' | 'failed' | 'skipped' | 'blocked';
  execution_date?: string;
  comments: string;
  execution_time_minutes?: number;
  notes: string;
}

export interface TestRun {
  id: number;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled';
  created_by: User;
  created_date: string;
  updated_date: string;
  scheduled_date?: string;
  test_executions: TestExecution[];
  execution_summary: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
    blocked: number;
    in_progress: number;
    not_executed: number;
    passed_percentage: number;
    failed_percentage: number;
    skipped_percentage: number;
    blocked_percentage: number;
  };
}

export interface DashboardStats {
  projects_count: number;
  epics_count: number;
  stories_count: number;
  testcases_count: number;
  test_runs_count: number;
  test_suites_count: number;
  total_executions: number;
  passed_executions: number;
  pass_rate: number;
  recent_executions_count: number;
  recent_projects: Project[];
  recent_testcases: TestCase[];
  recent_executions: TestExecution[];
}
