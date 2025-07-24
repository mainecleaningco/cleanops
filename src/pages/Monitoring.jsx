import React, { useState, useEffect } from 'react'
import { 
  Cpu, 
  HardDrive, 
  Wifi, 
  AlertTriangle, 
  CheckCircle, 
  AlertCircle,
  Activity
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

const Monitoring = () => {
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 72.5,
    memory: 68.3,
    disk: 34.7,
    network: 125.4
  })

  const [alerts] = useState([
    {
      id: 1,
      type: 'error',
      message: 'High memory usage detected on data processing node (85%)',
      timestamp: '2024-01-20T14:35:00Z',
      acknowledged: false
    },
    {
      id: 2,
      type: 'warning',
      message: 'Pipeline \'sales-report\' has been failing for the last 3 executions',
      timestamp: '2024-01-20T14:30:00Z',
      acknowledged: false
    },
    {
      id: 3,
      type: 'success',
      message: 'Data cleanup completed successfully - 2.8GB reclaimed',
      timestamp: '2024-01-20T14:25:00Z',
      acknowledged: true
    }
  ])

  const [performanceData] = useState([
    { time: '00:00', success: 95, executions: 24, dataProcessed: 0.8 },
    { time: '04:00', success: 98, executions: 18, dataProcessed: 1.2 },
    { time: '08:00', success: 92, executions: 32, dataProcessed: 2.1 },
    { time: '12:00', success: 96, executions: 28, dataProcessed: 1.8 },
    { time: '16:00', success: 94, executions: 22, dataProcessed: 1.5 },
    { time: '20:00', success: 97, executions: 26, dataProcessed: 1.9 },
  ])

  const [pipelineMetrics] = useState({
    totalExecutions24h: 156,
    successfulExecutions24h: 148,
    failedExecutions24h: 8,
    avgExecutionTime: 135.2,
    totalDataProcessed: 1.24,
    successRate: 94.87
  })

  // Simulate real-time metric updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.max(0, Math.min(100, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(0, Math.min(100, prev.memory + (Math.random() - 0.5) * 8)),
        disk: Math.max(0, Math.min(100, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.max(0, prev.network + (Math.random() - 0.5) * 20)
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getAlertIcon = (type) => {
    switch (type) {
      case 'error':
        return <AlertTriangle size={16} style={{ color: '#ef4444' }} />
      case 'warning':
        return <AlertCircle size={16} style={{ color: '#f59e0b' }} />
      case 'success':
        return <CheckCircle size={16} style={{ color: '#10b981' }} />
      default:
        return null
    }
  }

  const getProgressColor = (value) => {
    if (value > 80) return '#ef4444'
    if (value > 60) return '#f59e0b'
    return '#10b981'
  }

  return (
    <div className="monitoring">
      <div className="card-header">
        <h1 className="card-title">System Monitoring</h1>
        <div className="navbar-actions">
          <button className="btn btn-secondary">
            <Activity size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* System Resource Usage */}
      <div className="resource-usage">
        <div className="resource-item">
          <div className="resource-label">
            <Cpu size={20} style={{ marginRight: '8px' }} />
            CPU Usage
          </div>
          <div className="resource-value" style={{ color: getProgressColor(systemMetrics.cpu) }}>
            {systemMetrics.cpu.toFixed(1)}%
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${systemMetrics.cpu}%`,
                backgroundColor: getProgressColor(systemMetrics.cpu)
              }}
            ></div>
          </div>
        </div>

        <div className="resource-item">
          <div className="resource-label">
            <HardDrive size={20} style={{ marginRight: '8px' }} />
            Memory Usage
          </div>
          <div className="resource-value" style={{ color: getProgressColor(systemMetrics.memory) }}>
            {systemMetrics.memory.toFixed(1)}%
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${systemMetrics.memory}%`,
                backgroundColor: getProgressColor(systemMetrics.memory)
              }}
            ></div>
          </div>
        </div>

        <div className="resource-item">
          <div className="resource-label">
            <HardDrive size={20} style={{ marginRight: '8px' }} />
            Disk Usage
          </div>
          <div className="resource-value" style={{ color: getProgressColor(systemMetrics.disk) }}>
            {systemMetrics.disk.toFixed(1)}%
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${systemMetrics.disk}%`,
                backgroundColor: getProgressColor(systemMetrics.disk)
              }}
            ></div>
          </div>
        </div>

        <div className="resource-item">
          <div className="resource-label">
            <Wifi size={20} style={{ marginRight: '8px' }} />
            Network I/O
          </div>
          <div className="resource-value" style={{ color: '#3b82f6' }}>
            {systemMetrics.network.toFixed(1)} MB/s
          </div>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>
            Combined upload/download
          </div>
        </div>
      </div>

      {/* Pipeline Performance Metrics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#3b82f6' }}>
            {pipelineMetrics.totalExecutions24h}
          </div>
          <div className="stat-label">Total Executions (24h)</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#10b981' }}>
            {pipelineMetrics.successRate.toFixed(1)}%
          </div>
          <div className="stat-label">Success Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#6b7280' }}>
            {pipelineMetrics.avgExecutionTime.toFixed(0)}s
          </div>
          <div className="stat-label">Avg Duration</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#8b5cf6' }}>
            {pipelineMetrics.totalDataProcessed.toFixed(2)}TB
          </div>
          <div className="stat-label">Data Processed</div>
        </div>
      </div>

      {/* Performance Charts */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Pipeline Performance (Last 24h)</h2>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
          <div>
            <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Success Rate</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[80, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="success" stroke="#10b981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div>
            <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Data Processed (GB)</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="dataProcessed" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">System Alerts</h2>
          <span style={{ fontSize: '14px', color: '#6b7280' }}>
            {alerts.filter(alert => !alert.acknowledged).length} unacknowledged
          </span>
        </div>
        
        <div>
          {alerts.map(alert => (
            <div 
              key={alert.id} 
              className={`alert alert-${alert.type}`}
              style={{ 
                opacity: alert.acknowledged ? 0.6 : 1,
                marginBottom: '12px'
              }}
            >
              {getAlertIcon(alert.type)}
              <div style={{ flex: 1 }}>
                <div>{alert.message}</div>
                <small style={{ opacity: 0.7 }}>
                  {new Date(alert.timestamp).toLocaleString()}
                </small>
              </div>
              {!alert.acknowledged && (
                <button className="btn btn-secondary" style={{ fontSize: '12px' }}>
                  Acknowledge
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* System Health Overview */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">System Health</h2>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <CheckCircle size={48} style={{ color: '#10b981', marginBottom: '12px' }} />
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>Database</div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>Healthy</div>
          </div>
          
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <AlertCircle size={48} style={{ color: '#f59e0b', marginBottom: '12px' }} />
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>Queue System</div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>High Load</div>
          </div>
          
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <CheckCircle size={48} style={{ color: '#10b981', marginBottom: '12px' }} />
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>Storage</div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>Healthy</div>
          </div>
          
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <CheckCircle size={48} style={{ color: '#10b981', marginBottom: '12px' }} />
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>API Gateway</div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>Healthy</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Monitoring