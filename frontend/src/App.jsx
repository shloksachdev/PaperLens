import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import "./App.css";
import { uploadPDF, getNotes, askQuestion } from "./api";
import ReactMarkdown from "react-markdown";
import Login from "./Login";

function Dashboard({ onLogout }) {
  const [file, setFile] = useState(null);
  const [docId, setDocId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [query, setQuery] = useState("");

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadPDF(file);
      setDocId(data.doc_id);
      alert("File uploaded successfully.");
    } catch (error) {
      console.error(error);
      alert("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNotes = async () => {
    if (!docId) return;
    setLoading(true);
    try {
      const data = await getNotes(docId);
      setNotes(data);
    } catch (error) {
      console.error(error);
      alert("Error generating notes");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!docId || !query) return;
    const currentQuery = query;
    setChatHistory((prev) => [
      ...prev,
      { role: "user", content: currentQuery },
    ]);
    setQuery("");

    try {
      const data = await askQuestion(docId, currentQuery);
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", content: data.answer },
      ]);
    } catch (error) {
      console.error(error);
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", content: "Error getting answer." },
      ]);
    }
  };

  return (
    <div className="container">
      <header
        className="header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1>PaperLens</h1>
          <p>Research Paper Summarizer & Intelligence</p>
        </div>
        <button className="btn secondary" onClick={onLogout}>
          Logout
        </button>
      </header>

      <main className="main-content">
        <section className="card upload-section">
          <h2>Upload Research Paper</h2>
          <div className="upload-controls">
            <label className="file-input-label">
              <input type="file" accept=".pdf" onChange={handleFileChange} />
              <span>{file ? file.name : "Choose PDF File"}</span>
            </label>
            <button
              className="btn primary"
              onClick={handleUpload}
              disabled={loading || !file}
            >
              {loading ? "Processing..." : "Upload & Analyze"}
            </button>
          </div>
        </section>

        {docId && (
          <>
            <section className="actions">
              <button
                className="btn secondary"
                onClick={handleGenerateNotes}
                disabled={loading}
              >
                Generate Structured Analysis
              </button>
            </section>

            <div className="split-view">
              <div className="panel notes-panel">
                <div className="panel-header">
                  <h3>Analysis Results</h3>
                </div>
                {notes ? (
                  <div className="notes-content">
                    {Object.entries(notes).map(([section, content]) => (
                      <div key={section} className="note-section">
                        <h4>{section}</h4>
                        <ReactMarkdown>{content}</ReactMarkdown>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>
                      Select "Generate Structured Analysis" to view insights.
                    </p>
                  </div>
                )}
              </div>

              <div className="panel chat-panel">
                <div className="panel-header">
                  <h3>Q&A Interface</h3>
                </div>
                <div className="chat-history">
                  {chatHistory.length === 0 && (
                    <div className="empty-state">
                      <p>Ask specific questions about the paper.</p>
                    </div>
                  )}
                  {chatHistory.map((msg, idx) => (
                    <div key={idx} className={`chat-msg ${msg.role}`}>
                      <div className="msg-content">
                        <strong>
                          {msg.role === "user" ? "You" : "System"}
                        </strong>
                        <p>{msg.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="chat-input-area">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Type your question here..."
                    onKeyDown={(e) => e.key === "Enter" && handleChat()}
                  />
                  <button className="btn primary" onClick={handleChat}>
                    Send
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" />
            ) : (
              <Login onLogin={() => setIsAuthenticated(true)} />
            )
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Dashboard onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
