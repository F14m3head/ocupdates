import React from "react";

export default function Contact() {
  return (
    <main>
      <h2>Contact Us</h2>
      <form action="#">
        <label htmlFor="name">Name</label>
        <input type="text" id="name" required /><br />

        <label htmlFor="email">Email</label>
        <input type="text" id="email" required /><br />

        <label htmlFor="message">Message</label>
        <textarea id="message" rows={5}></textarea><br />

        <button type="submit">Send</button>
      </form>
    </main>
  );
} 