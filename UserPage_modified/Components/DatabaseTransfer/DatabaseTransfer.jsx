import React, { useState } from 'react';
import './DatabaseTransfer.css'; // Make sure to create and import the corresponding CSS file

const DatabaseTransfer = () => {
  const [isTransferring, setIsTransferring] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleTransfer = async () => {
    // Check if a file is selected before initiating the transfer
    if (!selectedFile) {
      alert('Please select a file before transferring data.');
      return;
    }

    // Implement your logic for transferring data to the database
    setIsTransferring(true);
    // Simulate an API request delay
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsTransferring(false);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    // Implement logic to handle the selected file (e.g., read and process the file)
    console.log('Selected File:', file);
  };

  return (
    <div className={`database-transfer ${isTransferring ? 'transferring' : ''}`}>
      <div className="form-container">
        <h2>Database Transfer</h2>
        <p>Upload a database file or click the button to transfer data to the database.</p>
        <input type="file" accept=".sql" onChange={handleFileChange} />
        <button onClick={handleTransfer} disabled={isTransferring}>
          {isTransferring ? 'Transferring...' : 'Transfer Data'}
        </button>
      </div>
    </div>
  );
};

export default DatabaseTransfer;
