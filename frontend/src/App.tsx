import { AdminApp } from './components/admin/AdminApp'
import { PortfolioPage } from './components/public/PortfolioPage'
import './App.css'

function App() {
  const isAdminRoute = window.location.pathname.startsWith('/admin')

  return isAdminRoute ? <AdminApp /> : <PortfolioPage />
}

export default App
