import { useState, useEffect } from "react";
import getWordOfDay from "./services/wordOfDay";
import getAppName from "./services/appName";

export default function App() {
  const [word, setWord] = useState("");
  const [appName, setAppName] = useState("");

  useEffect(() => {
    getWordOfDay()
      .then((data) => setWord(data.word))
      .catch(() => setWord("ERROR"));

    getAppName()
      .then((data) => setAppName(data.appName))
      .catch(() => setAppName("ERROR"));
  }, []);

  return (
    <>
      <h1>According to the backend of the <span className="app-name">{appName}</span> app, the word of the day is:</h1>
      <p>{word}</p>
    </>
  );
}