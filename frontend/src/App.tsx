import { AdminApp } from './components/admin/AdminApp'
import { PortfolioPage } from './components/public/PortfolioPage'
import { ProjectDetailPage } from './components/public/ProjectDetailPage'
import { getProjectRoute } from './routes'
import './App.css'

function App() {
  const isAdminRoute =
    window.location.pathname.startsWith('/admin') || window.location.pathname.startsWith('/dify/admin')

  if (isAdminRoute) {
    return <AdminApp />
  }

  const projectRoute = getProjectRoute(window.location.pathname)
  if (projectRoute) {
    return <ProjectDetailPage projectId={projectRoute.projectId} />
  }

  return <PortfolioPage />
}

export default App
