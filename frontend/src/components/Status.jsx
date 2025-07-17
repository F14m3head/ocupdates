import React from "react";

const statusCards = [
  {
    line: "O-Train Line 1",
    status: "Delayed",
    description: "Expect delays due to maintenance.",
    icon: "fa-train-subway",
    color: "#e67e22"
  },
  {
    line: "Bus Route 97",
    status: "On Time",
    description: "No reported issues.",
    icon: "fa-bus",
    color: "#27ae60"
  },
  {
    line: "Bus Route 85",
    status: "Detour",
    description: "Detour via Preston St. due to construction.",
    icon: "fa-road",
    color: "#f39c12"
  }
];

export default function Status() {
  return (
    <main className="status-container">
      <h1><i className="fas fa-signal"></i> System Status</h1>
      <p className="status-updated" id="lastUpdated">Updated just now</p>
      <div className="status-grid" id="statusGrid">
        {statusCards.map((card, idx) => (
          <div className="status-card" key={idx} style={{ borderLeft: `6px solid ${card.color}` }}>
            <h2><i className={`fas ${card.icon}`}></i> {card.line}</h2>
            <p><strong>Status:</strong> {card.status}</p>
            <p>{card.description}</p>
          </div>
        ))}
      </div>
      <div className="notice-box">
        <h2><i className="fas fa-exclamation-circle"></i> Notices</h2>
        <ul id="noticeList">
          <li>No major notices at this time.</li>
        </ul>
      </div>
    </main>
  );
} 