import React, { useState } from 'react';
import './ExternalSystemTransfer.css';

const ExternalSystemTransfer = () => {
  const [externalSystem, setExternalSystem] = useState('');
  const [isTransferring, setIsTransferring] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsTransferring(true);

    try {
      // Your logic for transferring data from the external system

      // Simulating an API request delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Reset form and animation after submission
      setExternalSystem('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsTransferring(false);
    }
  };

  return (
    <div className={`external-system-transfer ${isTransferring ? 'transferring' : ''}`}>
      <div className="form-container">
        <h2>Transfer from External System</h2>
        <form onSubmit={handleSubmit}>
          <label>
            External System:
            <input
              type="text"
              value={externalSystem}
              onChange={(e) => setExternalSystem(e.target.value)}
              required
            />
          </label>
          <button type="submit" className={isTransferring ? 'transferring' : ''}>
            {isTransferring ? 'Transferring...' : 'Transfer'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ExternalSystemTransfer;
