import { Link } from "react-router-dom";

export default function Footer() {
    return (
        <footer>
            <Link to="/faq"><i className="fas fa-question-circle"></i> FAQ</Link>
            <Link to="/contact"><i className="fas fa-envelope"></i> Contact</Link>
            &copy; 2025 ocUpdates
        </footer>
    );
} 