import { useState } from 'react';
import './App.css';
import FileUpload from './FileUpload/FileUpload';
import FileList from './FileList/FileList';
import InputBox from './inputBox';
import UserHeader from './UserHeader';


function App() {

  const [file, set_file] = useState([])

  const removeFile = (filename) => { set_file(file.filter(files =>files.name !== filename))}
  
  return (
    <div className="App">
      <div className="title">Welcome!</div>
      {/*User Header*/ }
      <div className='user-header-line'><UserHeader/>
      </div>

        {/*Input Box */}
        <div className='text-box-line'>
        <InputBox/>
        </div>
       
        {/*File Upload */}
        <div className="title 2 ">Upload File</div>
          <FileUpload file={file} setFiles={set_file} removeFile={removeFile}/>
            <FileList file={file} removeFile={removeFile} />
    </div>
    
  );
}

export default App;
