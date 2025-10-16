import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

function App() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // The official API is window.openai
    if (window.openai) {
      // Per the docs, UI-specific data is in toolResponseMetadata (_meta)
      const initialData = window.openai.toolResponseMetadata?.ui;
      if (initialData) {
        setData(initialData);
      }
      
      // It's good practice to listen for updates, though not strictly needed here
      const handleUpdate = (event) => {
        if (event.detail.globals.toolResponseMetadata) {
          setData(event.detail.globals.toolResponseMetadata.ui);
        }
      };
      
      window.addEventListener("openai:set_globals", handleUpdate);
      return () => {
        window.removeEventListener("openai:set_globals", handleUpdate);
      };

    } else {
      console.error('[Widget] window.openai is not available!');
    }
  }, []);
  
  // Read data from the correct fields based on our new backend structure
  const assignments = data?.assignments ?? [];
  const count = data?.count ?? 0;
  const rangeLabel = data?.rangeLabel || 'soon';
  const generatedAt = data?.generatedAt ? dayjs(data.generatedAt) : null;
  
  if (!data) {
    return (
      <div className="briefing-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading briefing...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="briefing-container">
      <header>
        <h3>📚 Daily Briefing</h3>
        {generatedAt && (
          <p className="timestamp" title={generatedAt.format('YYYY-MM-DD HH:mm:ss')}>
            Updated {generatedAt.fromNow()}
          </p>
        )}
      </header>
      
      <div className="summary-card">
        <div className="count">{count}</div>
        <div className="label">
          assignment{count !== 1 ? 's' : ''} due {rangeLabel}
        </div>
      </div>
      
      {assignments.length > 0 ? (
        <ul className="assignment-list">
          {assignments.map(item => (
            <li key={item.id}>
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                <div className="assignment-info">
                  <span className="title">{item.title}</span>
                  <span className="course">{item.course}</span>
                </div>
                <div className="due-date">
                  {item.dueAtDisplay}
                </div>
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <div className="empty-state">
          ✨ No upcoming assignments in this timeframe!
        </div>
      )}
    </div>
  );
}

export default App;