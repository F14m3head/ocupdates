import { Link } from "react-router-dom";
import React from "react";

export default function Home() {
  return (
    <main className="home-container">
      <section className="hero">
        <h1><i className="fas fa-bus"></i> OC Transit Tracker</h1>
        <p>Your unofficial source for real-time OC Transpo updates, schedules, and alerts.</p>
        <Link to="/faq" className="cta-button">Learn More</Link>
      </section>

      <section className="what-we-do">
        <h2><i className="fas fa-info-circle"></i> What We Do</h2>
        <p>We make it easy for Ottawa transit riders to access accurate bus and train info using open data and community updates.</p>
      </section>

      <section className="features">
        <h2><i className="fas fa-star"></i> Key Features</h2>
        <div className="feature-list">
          <div className="feature-item">
            <i className="fas fa-clock"></i>
            <h3>Live Updates</h3>
            <p>Stay informed about delays, detours, and transit alerts.</p>
          </div>
          <div className="feature-item">
            <i className="fas fa-robot"></i>
            <h3>Discord Bot</h3>
            <p>Join our server for real-time updates via our custom-built bot.</p>
          </div>
          <div className="feature-item">
            <i className="fas fa-map-marked-alt"></i>
            <h3>Route Info</h3>
            <p>Use our GTFS-powered tools to view accurate route schedules.</p>
          </div>
        </div>
      </section>

      <section className="call-to-action">
        <h2><i className="fas fa-users"></i> Join Our Community</h2>
        <p>Get live updates and help improve public transit for everyone in Ottawa.</p>
        <a href="https://discord.gg/eZrenwJt" className="cta-button">Join Our Discord</a>
      </section>
    </main>
  );
} 