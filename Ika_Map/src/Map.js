import React, { useEffect, useState } from 'react';
import './Map.css';


function Map() {
    // Stan przechowujący dane o mapie
    const [mapData, setMapData] = useState([]);
    const [hoveredCell, setHoveredCell] = useState(null);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
    // Funkcja do pobierania danych z API
    const fetchMapData = async () => {
      try {
        const response = await fetch('http://localhost:1090/api/map');
        const data = await response.json();
        setMapData(data);  // Zapisujemy dane o mapie w stanie
      } catch (error) {
        console.error('Błąd podczas pobierania danych:', error);
      }
    };

    const handleMouseEnter = (rowIndex, colIndex) => {
        if (mapData[rowIndex][colIndex] === 1) {
          setHoveredCell({ row: rowIndex+1, col: colIndex+1 });
        } else {
          setHoveredCell(null); // Jeśli to woda, usuń szczegóły
        }
    };

    const handleMouseMove = (event) => {
        setMousePosition({ x: event.clientX, y: event.clientY });
    };

    const handleMouseLeave = () => {
        setHoveredCell(null);
    };
  
    // useEffect działa jak componentDidMount, wykonujemy zapytanie po załadowaniu komponentu
    useEffect(() => {
      fetchMapData();
    }, []);  // Pusty array oznacza, że efekt uruchomi się tylko raz po renderze
  
    // Renderowanie mapy na podstawie danych
    return (
        <div className="Map">
        <table className="map-table">
            <tbody>
                {mapData.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                            <td
                                key={cellIndex}
                                className={cell === 1 ? 'island' : 'water'}
                                onMouseEnter={() => handleMouseEnter(rowIndex, cellIndex)}  // Obsługa najechania myszką
                                onMouseMove={handleMouseMove}
                                onMouseLeave={handleMouseLeave}  // Obsługa opuszczenia myszką
                            >
                                {/* Można dodać dodatkowe elementy */}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>

        {hoveredCell && (
            <div
                className="tooltip"
                style={{
                    position: 'absolute',
                    top: mousePosition.y + 10 + 'px', // Ustawiamy pozycję tooltipa tuż obok myszki
                    left: mousePosition.x + 10 + 'px',
                    backgroundColor: 'lightgray',
                    padding: '10px',
                    borderRadius: '5px',
                    boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)'
                }}
            >
                <h3>Wyspa na współrzędnych: ({hoveredCell.row}, {hoveredCell.col})</h3>
                <p>Szczegóły wyspy i dane graczy...</p>
            </div>
        )}
    </div>
    );
  }
  
  export default Map;