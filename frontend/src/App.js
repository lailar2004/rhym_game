import React, { useState, useEffect } from "react";
import "./App.css";

const Game = () => {
  const [word, setWord] = useState("");
  const [wordAudio, setWordAudio] = useState(null);
  const [options, setOptions] = useState([]);
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [correctAudio, setCorrectAudio] = useState(null);
  const [level, setLevel] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [totalAttempts, setTotalAttempts] = useState(0);
  const [startTime, setStartTime] = useState(null);
  const [answered, setAnswered] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchWord(level);
  }, [level]);

  const fetchWord = async (currentLevel) => {
    try {
      const response = await fetch(`http://localhost:5000/get_word?level=${currentLevel}`);
      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setWord(data.word);
      setWordAudio(data.word_audio);
      setOptions(shuffleArray(data.options));
      setCorrectAnswer(data.correct);
      setCorrectAudio(data.correct_audio);
      setStartTime(Date.now());
      setAnswered(false);
      setMessage("");

      playAudio(data.word_audio, data.word);
    } catch (error) {
      console.error("Error fetching word:", error);
    }
  };

  const handleAnswer = async (selectedWord) => {
    const endTime = Date.now();
    const timeTaken = (endTime - startTime) / 1000;
    const isCorrect = selectedWord === correctAnswer;

    setTotalAttempts(totalAttempts + 1);
    if (isCorrect) {
      setCorrectAnswers(correctAnswers + 1);
      setMessage("✅ Correct!");
      playAudio(correctAudio, correctAnswer);
    } else {
      setMessage(`❌ Wrong! The correct answer was: ${correctAnswer}`);
    }

    setAnswered(true);

    try {
      const response = await fetch("http://localhost:5000/submit_score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          level: level,
          time_taken: timeTaken,
          correct_answers: correctAnswers + (isCorrect ? 1 : 0),
          total_attempts: totalAttempts + 1,
        }),
      });

      const data = await response.json();
      if (data.next_level) {
        setLevel(data.next_level);
      }
    } catch (error) {
      console.error("Error predicting level:", error);
    }
  };

  const playAudio = (audioUrl, word) => {
    if (audioUrl) {
      const audio = new Audio(`http://localhost:5000${audioUrl}`);
      audio.play().catch((error) => console.error("Error playing audio:", error));
    } else {
      speakWord(word);
    }
  };

  const speakWord = (word) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(word);
      utterance.lang = "en-US";
      speechSynthesis.speak(utterance);
    } else {
      console.warn("Speech synthesis not supported in this browser.");
    }
  };

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <h2 className="logo">RhymeGame</h2>
        <ul className="nav-links">
          <li><a href="#">Home</a></li>
          <li><a href="#">Learn</a></li>
          <li><a href="#">Assessment</a></li>
          <li><a href="#">About Us</a></li>
\        </ul>
      </nav>

      {/* Game Container */}
      <div className="game-container">
        <h1>PICK THE RHYMING WORD</h1>

        <div className="score-box">Score: {correctAnswers} / {totalAttempts}</div>

        <div className="word-box">
          {word}
          <button className="speak-button" onClick={() => playAudio(wordAudio, word)}>🔊</button>
        </div>

        <div className="options">
          {options.map((opt, index) => (
            <div key={index} className="option-item">
              <button onClick={() => handleAnswer(opt)} disabled={answered}>
                {opt}
              </button>
              <button className="speak-button" onClick={() => playAudio(null, opt)}>🔊</button>
            </div>
          ))}
        </div>

        {message && <div className="message">{message}</div>}

        {answered && <button className="next-button" onClick={() => fetchWord(level)}>Next Word ➡</button>}
      </div>
    </div>
  );
};

const shuffleArray = (array) => {
  return [...array].sort(() => Math.random() - 0.5);
};

export default Game;
