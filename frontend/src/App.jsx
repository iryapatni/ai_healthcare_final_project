import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Shield, DollarSign, Calendar, Search, Loader2, Moon, Sun, MessageSquare, Plus, Trash2 } from 'lucide-react'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Theme state
  const [theme, setTheme] = useState('dark')
  
  // Chat history state
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('ai_planner_chats')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch (e) {
        return []
      }
    }
    return []
  })
  const [currentChatId, setCurrentChatId] = useState(null)

  // Save chats to localStorage
  useEffect(() => {
    localStorage.setItem('ai_planner_chats', JSON.stringify(chats))
  }, [chats])

  // Toggle theme
  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  // Apply theme to body
  useEffect(() => {
    document.body.className = theme
  }, [theme])

  // Get current active plan
  const currentChat = chats.find(c => c.id === currentChatId)
  const plan = currentChat?.plan

  const handleNewChat = () => {
    setCurrentChatId(null)
    setQuery('')
    setError(null)
  }

  const handleSelectChat = (id) => {
    setCurrentChatId(id)
    const selectedChat = chats.find(c => c.id === id)
    if (selectedChat) {
      setQuery(selectedChat.query)
      setError(null)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('http://localhost:8080/api/generate-plan', { query })
      
      const newPlan = response.data
      const newChatId = Date.now().toString()
      
      setChats(prev => [
        { id: newChatId, query, plan: newPlan },
        ...prev
      ])
      setCurrentChatId(newChatId)
      
    } catch (err) {
      console.error(err)
      let errorMessage = 'Failed to generate plan. Please try again later.'
      if (err.response && err.response.data) {
          try {
              // The rust backend forwards the python JSON as a text string
              const parsed = typeof err.response.data === 'string' ? JSON.parse(err.response.data) : err.response.data
              if (parsed.detail) errorMessage = parsed.detail
          } catch (e) {
              errorMessage = typeof err.response.data === 'string' ? err.response.data : errorMessage
          }
      }
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const formatText = (text) => {
    if (!text) return null;
    if (typeof text !== 'string') text = JSON.stringify(text);
    
    // Split by markdown bold tags
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className={`app-wrapper ${theme}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>AI Planner</h2>
          <button onClick={handleNewChat} className="icon-button" title="New Chat">
            <Plus size={20} />
          </button>
        </div>
        
        <div className="chat-history">
          {chats.length === 0 ? (
            <p className="empty-history">No past chats yet.</p>
          ) : (
            chats.map(chat => (
              <div key={chat.id} className={`history-item-container ${chat.id === currentChatId ? 'active' : ''}`}>
                <button 
                  className={`history-item`}
                  onClick={() => handleSelectChat(chat.id)}
                >
                  <MessageSquare size={16} />
                  <span className="history-text">{chat.query}</span>
                </button>
                <button 
                  className="delete-chat-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    const newChats = chats.filter(c => c.id !== chat.id);
                    setChats(newChats);
                    if (currentChatId === chat.id) handleNewChat();
                  }}
                  title="Delete Chat"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content-area">
        <header className="header">
          <div className="header-title">
            <h1>Healthcare & Insurance Planner</h1>
            <p>Intelligent guidance for your health and financial wellbeing</p>
          </div>
          <button onClick={toggleTheme} className="theme-toggle" title="Toggle Theme">
            {theme === 'dark' ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </header>

        <div className="content-wrapper">
          <form onSubmit={handleSearch} className="search-section">
            <input
              type="text"
              className="search-input"
              placeholder="E.g., I have diabetes, suggest treatment and insurance plan..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading || !query.trim()}>
              {loading ? <Loader2 className="spinner" size={20} /> : <Search size={20} />}
              <span>{loading ? 'Analyzing...' : 'Generate'}</span>
            </button>
          </form>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {loading && (
            <div className="loader">
              <Loader2 className="spinner" />
            </div>
          )}

          {plan && !loading && (
            <div className="results-grid">
              <div className="main-content">
                <div className="card">
                  <h2><Activity size={24} /> Treatment Plan</h2>
                  <p className="card-text">{formatText(plan.treatment_plan)}</p>
                </div>

                <div className="card">
                  <h2><Shield size={24} /> Insurance Suggestions</h2>
                  <p className="card-text">{formatText(plan.insurance_suggestions)}</p>
                </div>

                <div className="card">
                  <h2><Calendar size={24} /> Schedule & Cost</h2>
                  <div className="content-section">
                    <h3><DollarSign size={18} style={{display: 'inline', verticalAlign: 'text-bottom'}}/> Cost Estimation</h3>
                    <p>{formatText(plan.cost_estimation)}</p>
                  </div>
                  <div className="content-section">
                    <h3><Calendar size={18} style={{display: 'inline', verticalAlign: 'text-bottom'}}/> Recommended Schedule</h3>
                    <p>{formatText(plan.schedule)}</p>
                  </div>
                </div>
              </div>

              <div className="side-content">
                {plan.infographic_url && (
                  <div className="card image-container">
                    <h2>Visualization</h2>
                    <img src={plan.infographic_url} alt="Healthcare Infographic" />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
