import React, { useEffect } from "react";

export default function Map() {
  useEffect(() => {
    // Dynamically load Leaflet CSS
    const leafletCSS = document.createElement("link");
    leafletCSS.rel = "stylesheet";
    leafletCSS.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(leafletCSS);

    // Dynamically load Leaflet JS
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.async = true;
    script.onload = () => {
      const L = window.L;
      if (L) {
        const map = L.map("map").setView([45.4215, -75.6995], 12);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
          maxZoom: 18
        }).addTo(map);
        L.marker([45.4215, -75.6995])
          .addTo(map)
          .bindPopup("Downtown Ottawa")
          .openPopup();
      }
    };
    document.body.appendChild(script);
    return () => {
      // Clean up
      document.body.removeChild(script);
      document.head.removeChild(leafletCSS);
    };
  }, []);

  return (
    <>
      <section className="map-hero">
        <h1><i className="fas fa-map-marked-alt"></i> OC Transit Map</h1>
        <p>Explore Ottawa’s transit system with our interactive Leaflet map. Live data and routes coming soon.</p>
      </section>
      <main className="map-container">
        <div id="map" style={{ height: "400px", width: "100%" }}></div>
        <p className="map-footer-note">Powered by Leaflet & OpenStreetMap</p>
      </main>
    </>
  );
} 