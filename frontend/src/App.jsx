import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [mes, setMes] = useState("5");
  const [descargando, setDescargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !mes) {
      alert("Por favor selecciona un archivo y un mes.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("mes", mes);

    setDescargando(true);
    try {
      const response = await fetch("https://TU_BACKEND_URL/generar-archivo", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Error generando archivo");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `0125${mes.padStart(2, "0")}31.224`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      alert("Error: " + error.message);
    } finally {
      setDescargando(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Generador SUCAVE .224</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Archivo Excel (.xlsx):</label><br />
          <input type="file" accept=".xlsx" onChange={(e) => setFile(e.target.files[0])} />
        </div>
        <div style={{ marginTop: "1rem" }}>
          <label>Mes de la base:</label><br />
          <select value={mes} onChange={(e) => setMes(e.target.value)}>
            {[...Array(12)].map((_, i) => (
              <option key={i + 1} value={i + 1}>{i + 1}</option>
            ))}
          </select>
        </div>
        <div style={{ marginTop: "1.5rem" }}>
          <button type="submit" disabled={descargando}>
            {descargando ? "Generando..." : "Generar Archivo .224"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default App;
