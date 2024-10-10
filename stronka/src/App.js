import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  // Stan przechowujący dane o mapie
  const [mapData, setMapData] = useState([]);

  // Funkcja do pobierania danych z API
  const fetchMapData = async () => {
    try {
      const response = await fetch('http://localhost:1090/api/map');
      const data = await response.json();
      console.log(data);
      setMapData(data);  // Zapisujemy dane o mapie w stanie
    } catch (error) {
      console.error('Błąd podczas pobierania danych:', error);
    }
  };

  // useEffect działa jak componentDidMount, wykonujemy zapytanie po załadowaniu komponentu
  useEffect(() => {
    fetchMapData();
  }, []);  // Pusty array oznacza, że efekt uruchomi się tylko raz po renderze

  // Renderowanie mapy na podstawie danych
  return (
    <div className="App">
      <table className="map-table">
        <tbody>
          {mapData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td
                  key={cellIndex}
                  className={cell === 1 ? 'island' : 'water'}
                >
                  {/* Możemy dodać dodatkowe elementy, np. współrzędne */}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;