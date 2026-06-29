export type ProjectRoute = {
  projectId: number
}

export function getProjectRoute(pathname: string): ProjectRoute | null {
  const match = /^\/(?:dify\/)?projects\/([1-9]\d*)\/?$/.exec(pathname)
  if (!match) {
    return null
  }

  return {
    projectId: Number(match[1]),
  }
}

export function usesDifyBase(pathname: string) {
  return pathname === '/dify' || pathname.startsWith('/dify/')
}

export function projectDetailPath(projectId: number, currentPathname = window.location.pathname) {
  const prefix = usesDifyBase(currentPathname) ? '/dify' : ''
  return `${prefix}/projects/${projectId}`
}

export function portfolioHomePath(currentPathname = window.location.pathname) {
  return usesDifyBase(currentPathname) ? '/dify/' : '/'
}
