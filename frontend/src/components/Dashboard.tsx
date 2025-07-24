import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Button,
  Avatar,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Error,
  CheckCircle,
  Schedule,
  TrendingUp,
  Memory,
  Storage,
  Notifications,
  Refresh,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';

interface DashboardData {
  summary: {
    total_pipelines: number;
    active_pipelines: number;
    running_pipelines: number;
    failed_pipelines_24h: number;
    success_rate_24h: number;
    avg_execution_time_minutes: number;
  };
  recent_runs: Array<{
    id: string;
    pipeline_name: string;
    status: string;
    duration_minutes: number;
    started_at: string;
  }>;
  alerts_summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  resource_usage: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
  upcoming_schedules: Array<{
    schedule_name: string;
    pipeline_name: string;
    next_run: string;
  }>;
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Mock data for demonstration
  const mockData: DashboardData = {
    summary: {
      total_pipelines: 25,
      active_pipelines: 18,
      running_pipelines: 3,
      failed_pipelines_24h: 2,
      success_rate_24h: 94.2,
      avg_execution_time_minutes: 15.3,
    },
    recent_runs: [
      {
        id: 'run_456',
        pipeline_name: 'Customer Data ETL',
        status: 'completed',
        duration_minutes: 12.5,
        started_at: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
      },
      {
        id: 'run_457',
        pipeline_name: 'Log Aggregation',
        status: 'running',
        duration_minutes: 8.2,
        started_at: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
      },
      {
        id: 'run_458',
        pipeline_name: 'Data Validation',
        status: 'failed',
        duration_minutes: 5.1,
        started_at: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
      },
    ],
    alerts_summary: {
      critical: 0,
      high: 1,
      medium: 2,
      low: 0,
    },
    resource_usage: {
      cpu_percent: 45.2,
      memory_percent: 62.8,
      disk_percent: 34.1,
    },
    upcoming_schedules: [
      {
        schedule_name: 'Daily Customer Sync',
        pipeline_name: 'Customer ETL',
        next_run: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        schedule_name: 'Hourly Log Processing',
        pipeline_name: 'Log Aggregation',
        next_run: new Date(Date.now() + 45 * 60 * 1000).toISOString(),
      },
    ],
  };

  // Mock performance data for charts
  const performanceData = [
    { time: '00:00', success_rate: 95, execution_time: 12 },
    { time: '04:00', success_rate: 97, execution_time: 14 },
    { time: '08:00', success_rate: 93, execution_time: 18 },
    { time: '12:00', success_rate: 96, execution_time: 15 },
    { time: '16:00', success_rate: 94, execution_time: 16 },
    { time: '20:00', success_rate: 98, execution_time: 13 },
  ];

  const pipelineStatusData = [
    { name: 'Completed', value: 85, color: '#4caf50' },
    { name: 'Running', value: 8, color: '#2196f3' },
    { name: 'Failed', value: 5, color: '#f44336' },
    { name: 'Pending', value: 2, color: '#ff9800' },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDashboardData(mockData);
      setLoading(false);
    }, 1000);

    // Set up auto-refresh
    const interval = setInterval(() => {
      setLastUpdated(new Date());
      // In a real app, you'd fetch fresh data here
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const refreshData = () => {
    setLoading(true);
    setTimeout(() => {
      setDashboardData(mockData);
      setLastUpdated(new Date());
      setLoading(false);
    }, 500);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'running':
        return <PlayArrow color="primary" />;
      case 'failed':
        return <Error color="error" />;
      default:
        return <Schedule color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else {
      const diffHours = Math.floor(diffMins / 60);
      return `${diffHours}h ago`;
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading Dashboard...
        </Typography>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="error">
        Failed to load dashboard data. Please try again.
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          CleanOps Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <IconButton onClick={refreshData} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    Total Pipelines
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.summary.total_pipelines}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <TrendingUp />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    Success Rate (24h)
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {dashboardData.summary.success_rate_24h}%
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircle />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    Running Now
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {dashboardData.summary.running_pipelines}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <PlayArrow />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    Failed (24h)
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {dashboardData.summary.failed_pipelines_24h}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <Error />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Performance Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Trends (24h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="success_rate"
                    stroke="#4caf50"
                    strokeWidth={2}
                    name="Success Rate (%)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="execution_time"
                    stroke="#2196f3"
                    strokeWidth={2}
                    name="Avg Execution Time (min)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Pipeline Status Distribution */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Pipeline Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pipelineStatusData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {pipelineStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Pipeline Runs */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Pipeline Runs
              </Typography>
              <List>
                {dashboardData.recent_runs.map((run, index) => (
                  <React.Fragment key={run.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(run.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={run.pipeline_name}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={run.status}
                              size="small"
                              color={getStatusColor(run.status) as any}
                              variant="outlined"
                            />
                            <Typography variant="body2" color="text.secondary">
                              {run.duration_minutes}m • {formatTimeAgo(run.started_at)}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < dashboardData.recent_runs.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* System Resources */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Resources
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Memory sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" sx={{ minWidth: 60 }}>
                    CPU
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={dashboardData.resource_usage.cpu_percent}
                    sx={{ flexGrow: 1, mx: 2 }}
                    color="primary"
                  />
                  <Typography variant="body2">
                    {dashboardData.resource_usage.cpu_percent}%
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Memory sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="body2" sx={{ minWidth: 60 }}>
                    Memory
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={dashboardData.resource_usage.memory_percent}
                    sx={{ flexGrow: 1, mx: 2 }}
                    color="warning"
                  />
                  <Typography variant="body2">
                    {dashboardData.resource_usage.memory_percent}%
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Storage sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="body2" sx={{ minWidth: 60 }}>
                    Disk
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={dashboardData.resource_usage.disk_percent}
                    sx={{ flexGrow: 1, mx: 2 }}
                    color="success"
                  />
                  <Typography variant="body2">
                    {dashboardData.resource_usage.disk_percent}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts Summary */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Alerts
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {dashboardData.alerts_summary.critical > 0 && (
                  <Alert severity="error" icon={<Notifications />}>
                    {dashboardData.alerts_summary.critical} Critical alerts require immediate attention
                  </Alert>
                )}
                {dashboardData.alerts_summary.high > 0 && (
                  <Alert severity="warning" icon={<Notifications />}>
                    {dashboardData.alerts_summary.high} High priority alerts
                  </Alert>
                )}
                {dashboardData.alerts_summary.medium > 0 && (
                  <Alert severity="info" icon={<Notifications />}>
                    {dashboardData.alerts_summary.medium} Medium priority alerts
                  </Alert>
                )}
                {Object.values(dashboardData.alerts_summary).every(count => count === 0) && (
                  <Alert severity="success">
                    No active alerts - All systems operational
                  </Alert>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Schedules */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Schedules
              </Typography>
              <List>
                {dashboardData.upcoming_schedules.map((schedule, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemIcon>
                        <Schedule color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={schedule.schedule_name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Pipeline: {schedule.pipeline_name}
                            </Typography>
                            <Typography variant="body2" color="primary">
                              Next run: {new Date(schedule.next_run).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < dashboardData.upcoming_schedules.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;