import { useState, useEffect } from 'react'
import './App.css'
import { Newspaper, RefreshCcw, ExternalLink, Cpu, BookOpen, Search } from 'lucide-react'

interface NewsItem {
  title: string
  summary: string
  url: string
  category: string
  publish_date: string
  source: string
}

interface SourceStat {
  name: string
  today: number
  weekly: number
  monthly: number
  total: number
}

function App() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [sourceStats, setSourceStats] = useState<SourceStat[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [timeframe, setTimeframe] = useState<'today' | 'weekly' | 'monthly' | 'sources'>('today')

  const fetchNews = async (selectedTimeframe: string) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/news?timeframe=${selectedTimeframe}`)
      const data = await response.json()
      setNews(data.news)
      setLastUpdated(data.last_updated)
    } catch (error) {
      console.error('Error fetching news:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSourceStats = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/sources')
      const data = await response.json()
      setSourceStats(data.sources)
    } catch (error) {
      console.error('Error fetching sources:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      const refreshTimeframe = timeframe === 'sources' ? 'today' : timeframe
      const response = await fetch(`http://localhost:8000/api/refresh?timeframe=${refreshTimeframe}`, { method: 'POST' })
      const data = await response.json()
      if (data.status === 'success') {
        if (timeframe === 'sources') {
          await fetchSourceStats()
        } else {
          await fetchNews(timeframe)
        }
      }
    } catch (error) {
      console.error('Error refreshing:', error)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    if (timeframe === 'sources') {
      fetchSourceStats()
    } else {
      fetchNews(timeframe)
    }
  }, [timeframe])

  const getCategoryIcon = (category: string) => {
    if (category.toLowerCase().includes('tool')) return <Search size={18} />
    if (category.toLowerCase().includes('research')) return <BookOpen size={18} />
    return <Cpu size={18} />
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Newspaper size={32} className="logo-icon" />
            <h1>World of AI</h1>
          </div>
          <div className="header-actions">
            <div className="tabs">
              {(['today', 'weekly', 'monthly', 'sources'] as const).map((t) => (
                <button 
                  key={t}
                  className={`tab-btn ${timeframe === t ? 'active' : ''}`}
                  onClick={() => setTimeframe(t)}
                >
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>
            <button 
              className={`refresh-btn ${refreshing ? 'spinning' : ''}`}
              onClick={handleRefresh}
              disabled={refreshing || loading}
            >
              <RefreshCcw size={20} />
              <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="feed-info">
          {timeframe !== 'sources' && lastUpdated && (
            <span className="last-updated">
              Last updated: {new Date(lastUpdated).toLocaleString()}
            </span>
          )}
        </div>
        
        {loading ? (
          <div className="loader-container">
            <div className="pulse-loader"></div>
            <p>Gathering {timeframe} insights...</p>
          </div>
        ) : timeframe === 'sources' ? (
          <div className="sources-container">
            <table className="sources-table">
              <thead>
                <tr>
                  <th>Source Name</th>
                  <th>Today</th>
                  <th>Weekly</th>
                  <th>Monthly</th>
                  <th>Total Selected</th>
                </tr>
              </thead>
              <tbody>
                {sourceStats.map((source, index) => (
                  <tr key={index}>
                    <td className="source-name-cell">{source.name}</td>
                    <td>{source.today}</td>
                    <td>{source.weekly}</td>
                    <td>{source.monthly}</td>
                    <td className="total-cell">{source.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="news-grid">
            {news.map((item, index) => (
              <article key={index} className="news-card">
                <div className="card-category">
                  <div className="category-left">
                    {getCategoryIcon(item.category)}
                    <span>{item.category}</span>
                  </div>
                  <span className="publish-date">{item.publish_date}</span>
                </div>
                <h3>{item.title}</h3>
                <p>{item.summary}</p>
                <div className="card-footer">
                  <span className="news-source">{item.source}</span>
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="read-more">
                    Read Story <ExternalLink size={14} />
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2026 World of AI. Powered by Tavily & Gemini 3.1.</p>
      </footer>
    </div>
  )
}

export default App
