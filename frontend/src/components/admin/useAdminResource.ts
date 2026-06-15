import { useCallback, useEffect, useState } from 'react'

export function useAdminResource<T>(loader: () => Promise<T>, initialValue: T) {
  const [data, setData] = useState<T>(initialValue)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const reload = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setData(await loader())
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }, [loader])

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      void reload()
    }, 0)
    return () => window.clearTimeout(timeout)
  }, [reload])

  return { data, setData, loading, error, reload, setError }
}
