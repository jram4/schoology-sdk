import React, { useState, useEffect, useMemo } from 'react';
import dayjs from 'dayjs';
import calendar from 'dayjs/plugin/calendar';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(calendar);
dayjs.extend(relativeTime);

// A helper function to create date groups
const groupAssignmentsByDay = (assignments) => {
  if (!assignments || assignments.length === 0) {
    return {};
  }
  
  const grouped = assignments.reduce((acc, assignment) => {
    // dayjs().calendar() is powerful. It returns strings like:
    // "Today at 11:59 PM", "Tomorrow at 1:55 PM", "Last Friday at 2:00 PM", "10/17/2025"
    // We can split on " at " to get just the day part.
    const dayKey = dayjs(assignment.dueAt).calendar(null, {
      sameDay: '[Today]',
      nextDay: '[Tomorrow]',
      nextWeek: 'dddd, MMM D', // e.g., "Friday, Oct 17"
      sameElse: 'MMM D, YYYY'
    });
    
    if (!acc[dayKey]) {
      acc[dayKey] = [];
    }
    acc[dayKey].push(assignment);
    return acc;
  }, {});

  return grouped;
};


function App() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    if (window.openai) {
      const initialData = window.openai.toolResponseMetadata?.ui;
      if (initialData) {
        setData(initialData);
      }
      
      const handleUpdate = (event) => {
        if (event.detail.globals.toolResponseMetadata) {
          setData(event.detail.globals.toolResponseMetadata.ui);
        }
      };
      
      window.addEventListener("openai:set_globals", handleUpdate);
      return () => {
        window.removeEventListener("openai:set_globals", handleUpdate);
      };
    }
  }, []);
  
  const assignments = data?.assignments ?? [];
  const count = data?.count ?? 0;
  const rangeLabel = data?.rangeLabel || 'soon';
  const generatedAt = data?.generatedAt ? dayjs(data.generatedAt) : null;
  
  // useMemo will cache the result of grouping so it doesn't re-run on every render
  const groupedAssignments = useMemo(() => groupAssignmentsByDay(assignments), [assignments]);
  
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
        <div className="grouped-assignments">
          {Object.entries(groupedAssignments).map(([day, items]) => (
            <div key={day} className="day-group">
              <h4 className="day-header">{day}</h4>
              <ul className="assignment-list">
                {items.map(item => (
                  <li key={item.id}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      <div className="assignment-info">
                        <div className="title-wrapper">
                          {item.type !== 'Homework' && (
                            <span className={`badge type-${item.type.toLowerCase()}`}>{item.type}</span>
                          )}
                          <span className="title">{item.title}</span>
                        </div>
                        <span className="course">{item.course}</span>
                      </div>
                      <div className="due-date">
                        {dayjs(item.dueAt).format('h:mm a')}
                      </div>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          ✨ No upcoming assignments in this timeframe!
        </div>
      )}
    </div>
  );
}

export default App;