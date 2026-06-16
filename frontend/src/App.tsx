import { AdminApp } from './components/admin/AdminApp'
import { PortfolioPage } from './components/public/PortfolioPage'
import './App.css'

function App() {
  const isAdminRoute =
    window.location.pathname.startsWith('/admin') || window.location.pathname.startsWith('/dify/admin')

  return isAdminRoute ? <AdminApp /> : <PortfolioPage />
}

export default App
