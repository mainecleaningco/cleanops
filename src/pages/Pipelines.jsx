import React, { useState } from 'react'
import { Plus, Edit, Trash2, Play, Settings } from 'lucide-react'

const Pipelines = () => {
  const [selectedPipeline, setSelectedPipeline] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  const [pipelines] = useState([
    {
      id: 1,
      name: 'user-data-etl',
      description: 'Daily user data processing and cleanup',
      status: 'active',
      schedule: '0 2 * * *',
      lastRun: '2024-01-20T14:30:00Z',
      dataSource: 'PostgreSQL',
      destination: 'Data Warehouse'
    },
    {
      id: 2,
      name: 'cleanup-logs',
      description: 'Automated log cleanup and archival',
      status: 'active',
      schedule: '0 0 * * 0',
      lastRun: '2024-01-19T00:00:00Z',
      dataSource: 'File System',
      destination: 'Archive Storage'
    },
    {
      id: 3,
      name: 'sales-report',
      description: 'Weekly sales data aggregation',
      status: 'inactive',
      schedule: '0 6 * * 1',
      lastRun: '2024-01-15T06:00:00Z',
      dataSource: 'MySQL',
      destination: 'Analytics DB'
    }
  ])

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    dataSource: 'postgresql',
    connection: 'prod-db',
    query: '',
    schedule: '0 2 * * *',
    timezone: 'UTC',
    active: true
  })

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('Creating pipeline:', formData)
    setShowCreateForm(false)
    // Reset form
    setFormData({
      name: '',
      description: '',
      dataSource: 'postgresql',
      connection: 'prod-db',
      query: '',
      schedule: '0 2 * * *',
      timezone: 'UTC',
      active: true
    })
  }

  return (
    <div className="pipelines">
      <div className="card-header">
        <h1 className="card-title">Pipeline Management</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          <Plus size={16} />
          Create Pipeline
        </button>
      </div>

      {showCreateForm && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Create New Pipeline</h2>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Pipeline Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="form-input"
                placeholder="e.g., user-data-etl"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="form-textarea"
                placeholder="Brief description of what this pipeline does"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Data Source Type</label>
              <select
                name="dataSource"
                value={formData.dataSource}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="mongodb">MongoDB</option>
                <option value="api">REST API</option>
                <option value="file">File System</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Connection</label>
              <select
                name="connection"
                value={formData.connection}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="prod-db">Production Database</option>
                <option value="staging-db">Staging Database</option>
                <option value="analytics-db">Analytics Database</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Query/Source Configuration</label>
              <textarea
                name="query"
                value={formData.query}
                onChange={handleInputChange}
                className="form-textarea"
                placeholder="SELECT * FROM users WHERE updated_at > ?"
                style={{ minHeight: '100px' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Schedule (Cron Expression)</label>
              <input
                type="text"
                name="schedule"
                value={formData.schedule}
                onChange={handleInputChange}
                className="form-input"
                placeholder="0 2 * * *"
              />
              <small style={{ color: '#6b7280', fontSize: '12px' }}>
                Examples: "0 2 * * *" (daily at 2 AM), "0 0 * * 0" (weekly on Sunday)
              </small>
            </div>

            <div className="form-group">
              <label className="form-label">Timezone</label>
              <select
                name="timezone"
                value={formData.timezone}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
              </select>
            </div>

            <div className="form-group">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="active"
                  checked={formData.active}
                  onChange={handleInputChange}
                  id="active-checkbox"
                />
                <label htmlFor="active-checkbox" className="form-label">
                  Active (pipeline will run according to schedule)
                </label>
              </div>
            </div>

            <div className="form-group">
              <button type="submit" className="btn btn-primary">
                Create Pipeline
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => setShowCreateForm(false)}
                style={{ marginLeft: '12px' }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Pipelines */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Existing Pipelines</h2>
        </div>
        
        <table className="pipeline-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Status</th>
              <th>Schedule</th>
              <th>Data Source</th>
              <th>Last Run</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pipelines.map(pipeline => (
              <tr key={pipeline.id}>
                <td><strong>{pipeline.name}</strong></td>
                <td>{pipeline.description}</td>
                <td>
                  <span className={`status-badge status-${pipeline.status === 'active' ? 'success' : 'scheduled'}`}>
                    {pipeline.status}
                  </span>
                </td>
                <td><code>{pipeline.schedule}</code></td>
                <td>{pipeline.dataSource}</td>
                <td>{new Date(pipeline.lastRun).toLocaleString()}</td>
                <td>
                  <div className="actions">
                    <button className="btn btn-primary">
                      <Play size={12} />
                    </button>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => setSelectedPipeline(pipeline)}
                    >
                      <Edit size={12} />
                    </button>
                    <button className="btn btn-secondary">
                      <Settings size={12} />
                    </button>
                    <button className="btn btn-danger">
                      <Trash2 size={12} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedPipeline && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Pipeline Details - {selectedPipeline.name}</h2>
            <button 
              className="btn btn-secondary"
              onClick={() => setSelectedPipeline(null)}
            >
              Close
            </button>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h3>Configuration</h3>
              <p><strong>Name:</strong> {selectedPipeline.name}</p>
              <p><strong>Description:</strong> {selectedPipeline.description}</p>
              <p><strong>Schedule:</strong> <code>{selectedPipeline.schedule}</code></p>
              <p><strong>Status:</strong> {selectedPipeline.status}</p>
            </div>
            <div>
              <h3>Data Flow</h3>
              <p><strong>Source:</strong> {selectedPipeline.dataSource}</p>
              <p><strong>Destination:</strong> {selectedPipeline.destination}</p>
              <p><strong>Last Run:</strong> {new Date(selectedPipeline.lastRun).toLocaleString()}</p>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <h3>Transformation Steps</h3>
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '6px' }}>
              <ol>
                <li>Data Validation - Check required fields and data types</li>
                <li>PII Anonymization - Hash sensitive information</li>
                <li>Data Enrichment - Add computed fields and metadata</li>
                <li>Quality Checks - Validate data integrity</li>
              </ol>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Pipelines