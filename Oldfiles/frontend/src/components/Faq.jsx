import React from "react";

export default function Faq() {
  return (
    <main className="faq-container">
      <h1>Frequently Asked Questions</h1>
      <div className="faq-item">
        <h2><i className="fas fa-info-circle"></i> What is this project?</h2>
        <p>A community-built tool to view OC Transpo updates, schedules, and alerts using GTFS data and a custom bot.</p>
      </div>
      <div className="faq-item">
        <h2><i className="fas fa-link"></i> Is this official?</h2>
        <p>No. This project is not affiliated with OC Transpo or the City of Ottawa. It's an independent volunteer-run system.</p>
      </div>
      <div className="faq-item">
        <h2><i className="fas fa-clock"></i> How often is the data updated?</h2>
        <p>Route schedules are synced daily. Real-time alerts are updated as they come in.</p>
      </div>
      <div className="faq-item">
        <h2><i className="fab fa-discord"></i> Where can I join the Discord?</h2>
        <p><a href="https://discord.gg/eZrenwJt" target="_blank" rel="noopener noreferrer">Click here to join the Discord server</a></p>
      </div>
      <div className="faq-item">
        <h2><i className="fas fa-bug"></i> Can I report a bug or suggest a feature?</h2>
        <p>Yes! Visit the Contact page or submit an issue on <a href="https://github.com/yourproject" target="_blank" rel="noopener noreferrer">GitHub</a>.</p>
      </div>
      <div className="faq-item">
        <h2><i className="fas fa-users"></i> Who built this?</h2>
        <p>A few transit-loving developers from Ottawa. Learn more on the Work page.</p>
      </div>
    </main>
  );
} 