import { Link } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { FaMoon, FaSun } from "react-icons/fa";

export default function Header() {
    const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

    useEffect(() => {
        document.body.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
    }, [theme]);

    const handleToggle = () => {
        setTheme((prev) => (prev === "dark" ? "light" : "dark"));
    };

    return (
        <header>
            <h1><i className="fas fa-bus"></i>ocUpdates</h1>
            <nav className="header-nav">
                <Link to="/" ><i className="fas fa-home"></i> Home</Link>
                <Link to="/status" ><i className="fas fa-bolt"></i> Status</Link>
                <Link to="/map" ><i className="fas fa-map"></i> Map</Link>
                <button id="toggleDarkMode" onClick={handleToggle}>
                    {theme === "dark" ? <FaSun /> : <FaMoon />}
                </button>
            </nav>
        </header>
    );
}