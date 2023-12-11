import React, { useState } from 'react';
import './BatchInputForm.css';

const BatchInputForm = () => {
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check if a file is selected before initiating the submission
    if (!file) {
      alert('Please select a file before submitting data.');
      return;
    }

    setIsSubmitting(true);

    try {
      // Your logic for submitting data to the backend

      // Simulating an API request delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Reset form and animation after submission
      setFile(null);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`batch-input-form ${isSubmitting ? 'submitting' : ''}`}>
      <div className="form-container">
        <h2>Batch Input</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Upload File:
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              accept=".txt, .csv, .json"
              required
            />
          </label>
          <button type="submit" className={isSubmitting ? 'submitting' : ''}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BatchInputForm;
