import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { getFirestore } from 'firebase/firestore'; // Import the 'getFirestore' function
import './AnalysisChart.css';

const MusicDashboard = () => {
    const [songData, setSongData] = useState([]);
    const [selectedPeriod, setSelectedPeriod] = useState('90s');
    const [chartData, setChartData] = useState({});

    useEffect(() => {
        const fetchData = async () => {
            try {
                const db = getFirestore();
                const data = await db.collection('songs').get();
        
                if (!data.empty) {
                    setSongData(data.docs.map(doc => doc.data()));
                    // Additional data processing and analysis here
                } else {
                    console.log('No data found in the collection.');
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        

        fetchData();
    }, []);

    useEffect(() => {
        const updateChartData = () => {
            // Create chart data based on songData and selectedPeriod
            // This is a placeholder function, you'll need to implement the actual logic
        };

        updateChartData();
    }, [songData, selectedPeriod]);

    const handlePeriodChange = (event) => {
        setSelectedPeriod(event.target.value);
    };

    return (
        <div className="container">
            <h2>Music Dashboard</h2>

            <div className="select-container">
                <label>Select Period:</label>
                <select value={selectedPeriod} onChange={handlePeriodChange}>
                    <option value="90s">90s</option>
                    {/* Additional period options here */}
                </select>
            </div>

            <div className="chart-container">
                <Line data={chartData} />
            </div>
        </div>
    );
};

export default MusicDashboard;
