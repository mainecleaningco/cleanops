import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Pipeline, 
  Activity, 
  Settings, 
  Bell,
  Database,
  BarChart3
} from 'lucide-react'
import './Navbar.css'

const Navbar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/pipelines', icon: Pipeline, label: 'Pipelines' },
    { path: '/monitoring', icon: Activity, label: 'Monitoring' },
    { path: '/data', icon: Database, label: 'Data Sources' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-header">
        <h1 className="navbar-title">CleanOps</h1>
        <div className="navbar-subtitle">Data Pipeline Management</div>
      </div>
      
      <ul className="navbar-menu">
        {navItems.map(({ path, icon: Icon, label }) => (
          <li key={path}>
            <Link 
              to={path} 
              className={`navbar-link ${location.pathname === path ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          </li>
        ))}
      </ul>

      <div className="navbar-footer">
        <div className="navbar-user">
          <div className="user-avatar">A</div>
          <div className="user-info">
            <div className="user-name">Admin User</div>
            <div className="user-role">System Administrator</div>
          </div>
        </div>
        
        <div className="navbar-actions">
          <button className="navbar-action-btn">
            <Bell size={18} />
          </button>
          <button className="navbar-action-btn">
            <Settings size={18} />
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar