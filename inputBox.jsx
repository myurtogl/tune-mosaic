import React, { useState } from 'react';
import './InputBox.scss';

const InputBox = () => {
  const [inputValue, setInputValue] = useState('');
  const [inputSize, setInputSize] = useState('25px'); // Initial size, you can adjust as needed


  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const showInputValue = () => {
    alert(`You entered: ${inputValue}`);
  };
  const changeInputSize = (newSize) => {
    setInputSize(newSize);
  };

  return (
    <div> 
      <h1>Enter Song </h1>
      <input
        type="text"
        id="userInput"
        placeholder="Enter song info      "
        value={inputValue}
        onChange={handleInputChange}
        style={{ fontSize: inputSize }} // Set the font size dynamically

      />
      <button onClick={showInputValue}>Submit</button>
    </div>
  );
};

export default InputBox;
