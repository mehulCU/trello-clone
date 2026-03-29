import React from "react";
import Board from "./components/Board";

function App() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Trello Clone</h1>

      {/* ✅ ONLY ONE BOARD COMPONENT */}
      <Board />
    </div>
  );
}

export default App;