import React, { useState } from 'react';
import './RemoveItem.css';

const RemoveItem = () => {
  const [itemToRemove, setItemToRemove] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Your logic for removing item from the backend

      // Simulating an API request delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Reset form and animation after submission
      setItemToRemove('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`remove-item ${isSubmitting ? 'submitting' : ''}`}>
      <div className="form-container">
        <h2>Remove Item</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Item to Remove:
            <input
              type="text"
              value={itemToRemove}
              onChange={(e) => setItemToRemove(e.target.value)}
              required
            />
          </label>
          <button type="submit" className={isSubmitting ? 'submitting' : ''}>
            {isSubmitting ? 'Removing...' : 'Remove'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default RemoveItem;
