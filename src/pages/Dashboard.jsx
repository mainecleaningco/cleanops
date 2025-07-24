import React, { useState, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  RotateCcw, 
  BarChart3, 
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react'

const Dashboard = () => {
  const [pipelines, setPipelines] = useState([
    {
      id: 1,
      name: 'user-data-etl',
      status: 'success',
      duration: '2m 34s',
      lastRun: '10:30 AM',
      progress: 100
    },
    {
      id: 2,
      name: 'cleanup-logs',
      status: 'running',
      duration: '1m 12s',
      lastRun: '10:25 AM',
      progress: 65
    },
    {
      id: 3,
      name: 'sales-report',
      status: 'failed',
      duration: '0m 45s',
      lastRun: '10:20 AM',
      progress: 0
    },
    {
      id: 4,
      name: 'inventory-sync',
      status: 'scheduled',
      duration: '3m 22s',
      lastRun: '09:45 AM',
      progress: 0
    },
    {
      id: 5,
      name: 'analytics-aggregation',
      status: 'success',
      duration: '4m 18s',
      lastRun: '09:30 AM',
      progress: 100
    }
  ])

  const [stats, setStats] = useState({
    running: 1,
    scheduled: 12,
    failed: 3,
    completed: 156
  })

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={16} className="text-green-600" />
      case 'running':
        return <Play size={16} className="text-blue-600" />
      case 'failed':
        return <XCircle size={16} className="text-red-600" />
      case 'scheduled':
        return <Clock size={16} className="text-yellow-600" />
      default:
        return null
    }
  }

  const handlePipelineAction = (id, action) => {
    setPipelines(prev => prev.map(pipeline => {
      if (pipeline.id === id) {
        switch (action) {
          case 'pause':
            return { ...pipeline, status: 'paused' }
          case 'resume':
            return { ...pipeline, status: 'running', progress: 0 }
          case 'restart':
            return { ...pipeline, status: 'running', progress: 0 }
          default:
            return pipeline
        }
      }
      return pipeline
    }))
  }

  // Simulate progress updates for running pipelines
  useEffect(() => {
    const interval = setInterval(() => {
      setPipelines(prev => prev.map(pipeline => {
        if (pipeline.status === 'running' && pipeline.progress < 100) {
          return { ...pipeline, progress: Math.min(pipeline.progress + 5, 100) }
        }
        return pipeline
      }))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="dashboard">
      <div className="card-header">
        <h1 className="card-title">CleanOps Dashboard</h1>
        <div className="navbar-actions">
          <button className="btn btn-primary">
            <Play size={16} />
            Run Pipeline
          </button>
        </div>
      </div>

      {/* Pipeline Status Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#3b82f6' }}>{stats.running}</div>
          <div className="stat-label">Running</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#f59e0b' }}>{stats.scheduled}</div>
          <div className="stat-label">Scheduled</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#ef4444' }}>{stats.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#10b981' }}>{stats.completed}</div>
          <div className="stat-label">Completed</div>
        </div>
      </div>

      {/* Recent Pipeline Executions */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Pipeline Executions</h2>
        </div>
        
        <table className="pipeline-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Last Run</th>
              <th>Progress</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pipelines.map(pipeline => (
              <tr key={pipeline.id}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getStatusIcon(pipeline.status)}
                    <strong>{pipeline.name}</strong>
                  </div>
                </td>
                <td>
                  <span className={`status-badge status-${pipeline.status}`}>
                    {pipeline.status.charAt(0).toUpperCase() + pipeline.status.slice(1)}
                  </span>
                </td>
                <td>{pipeline.duration}</td>
                <td>{pipeline.lastRun}</td>
                <td>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${pipeline.progress}%` }}
                    ></div>
                  </div>
                  <small>{pipeline.progress}%</small>
                </td>
                <td>
                  <div className="actions">
                    {pipeline.status === 'running' ? (
                      <button 
                        className="btn btn-secondary"
                        onClick={() => handlePipelineAction(pipeline.id, 'pause')}
                      >
                        <Pause size={12} />
                      </button>
                    ) : pipeline.status === 'paused' ? (
                      <button 
                        className="btn btn-success"
                        onClick={() => handlePipelineAction(pipeline.id, 'resume')}
                      >
                        <Play size={12} />
                      </button>
                    ) : (
                      <button 
                        className="btn btn-primary"
                        onClick={() => handlePipelineAction(pipeline.id, 'restart')}
                      >
                        <RotateCcw size={12} />
                      </button>
                    )}
                    <button className="btn btn-secondary">
                      <BarChart3 size={12} />
                    </button>
                    {pipeline.status === 'failed' && (
                      <button className="btn btn-danger">
                        <AlertTriangle size={12} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* System Alerts */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">System Alerts</h2>
        </div>
        
        <div className="alert alert-error">
          <AlertTriangle size={16} />
          <span>High memory usage detected on data processing node (85%)</span>
        </div>
        
        <div className="alert alert-warning">
          <Clock size={16} />
          <span>Pipeline 'sales-report' has been failing for the last 3 executions</span>
        </div>
        
        <div className="alert alert-success">
          <CheckCircle size={16} />
          <span>Data cleanup completed successfully - 2.8GB reclaimed</span>
        </div>
      </div>
    </div>
  )
}

export default Dashboard