import logo from './logo.svg';
import {useState,useRef} from 'react'
import 'react-toastify/dist/ReactToastify.css';
import {toast} from 'react-toastify';

import './App.css';

function App() {
  const [received,setReceived]=useState(false) //boolean to indicate whether results are received
  const [results,setResults]=useState(null) // hold the received results
  const [loading,setLoading]=useState(false)  // boolean to indicate results are being generated
  const [choice,setChoice]=useState(null) // boolean to indicate query choice e.g. date
  const [exception,setException]=useState(null) // hold the exception like if there are no GTT breaks
  const [filesToUpload,setFiles]=useState(null) // hold the files to be uploaded
  const [uploading,setUploading]=useState(false) // boolean to indicate if files are being uploaded
  const date=useRef(null) // ref to hold date input
  const trade=useRef(null) // ref to hold trade id input
  const client=useRef(null) //ref to hold client id input
  const resultsList=useRef(null) // ref to hold results section div
  toast.configure({className: 'toastBackground',
    bodyClassName:'toastBody',
    position:toast.POSITION.TOP_CENTER,
  })

  // Handle change in uploaded files chosen
  const handleChange = event => {
    let result=Object.keys(event.target.files).map((key)=>event.target.files[key])
    setFiles(event.target.files)
  };
 
  // Upload files to database
  const submit=async()=>{
    // If no files selected for upload
    if (filesToUpload==null){
      toast('Please choose a file to upload!')
      return
    }
    setUploading(true)    
    
    // Append files to be uploaded to FormData
    const formData = new FormData();
    const files =filesToUpload;
  
    for (let i = 0; i < files.length; i++) {
    formData.append('files[]',files[i])
      }

    await fetch(`http://127.0.0.1:8000/upload_files`,{
      body:formData,
      method:'POST'
    }).then(
      response=>response.json()
    ).then(data=>{
      setUploading(false)
      toast(data.message, 
        {position: toast.POSITION.TOP_CENTER})})
      .catch(e=>{
        toast(e.toString())})}

  // Query by date
  const getDates=async(date)=>{
    if (!date || date==''){
      toast('Please enter a date!')
      return
    }
    setChoice(`GTT Breaks for Date: ${date}`)
    setException(null)
    setLoading(true)
    setReceived(false)
    await fetch(`http://127.0.0.1:8000/get_by_date?date=${date}`,{
      method:'GET'
    }).then(
      response=>response.json()
    ).then(data=>{
      if (data.data){
        setResults(data.data)
      setReceived(true)
      setLoading(false)
      console.log(data.data)
      resultsList.current.scrollIntoView({ behavior: "smooth",  })
      }
      else{
        setLoading(false)
        setException('All clients are GTT for all trades on the given date')
      }
      
    })
  }

  // Query by trade
  const getTrades=async(trade)=>{
    if (!trade || trade==''){
      toast('Please enter a trade id!')
      return
    }
    setChoice(`GTT Breaks for Trade ID: ${trade}`)
    setException(null)
    setLoading(true)
    setReceived(false)
    await fetch(`http://127.0.0.1:8000/get_by_trade?trade=${trade}`,{
      method:'GET'
    }).then(
      response=>response.json()
    ).then(data=>{
      if (data.data){
        setResults(data.data)
      setReceived(true)
      setLoading(false)
      console.log(data.data)
      resultsList.current.scrollIntoView({ behavior: "smooth",  })

      }
      else{
        setLoading(false)
        setException('The trade is GTT')
      }
      
    })
  }

  // Query by client
  const getClient=async(client)=>{
    if (!client || client==''){
      toast('Please enter a client id!')
      return
    }
    setChoice(`GTT Breaks for Client ID: ${client}`)
    setException(null)
    setLoading(true)
    setReceived(false)
    await fetch(`http://127.0.0.1:8000/get_by_client?client=${client}`,{
      method:'GET'
    }).then(
      response=>response.json()
    ).then(data=>{
      if (data.data){
      setResults(data.data)
      setReceived(true)
      setLoading(false)
      console.log(data.data)
      resultsList.current.scrollIntoView({ behavior: "smooth",  })
      }
      else{
        setLoading(false)
        setException('Client is GTT for all in scope FNB entities')
      }
    })
  }

  return (
    <div className="App">
      {loading&&<div className='progress'><div class="loader"></div><div></div><p>Loading</p></div>}
      {uploading&&<div className='progress'><div class="loader"></div><div></div><p>Uploading<br></br>file</p></div>}
      <div style={{'color':'blue','fontWeight':'bold','paddingBottom':'10px','paddingTop':'10px','backgroundColor':'whitesmoke',
      'fontSize':'7.5vmin','borderBottom':'1px solid #000000'}}>GTT Search</div>
      <div style={{'margin':'20px'}}>
      <input
      id='file-upload'
      type="file"
      name="file"
      placeholder={null}
      onChange={handleChange}
      multiple
      />
      <button onClick={submit}>Upload File</button>
      </div>
      <fieldset style={{'width':'fit-content','marginLeft':'auto','marginRight':'auto','display':'flex',
    'flexDirection':'column','justifyContent':'center','alignContent':'center','alignItems':'center','padding':'20px'}}>
      <fieldset style={{'display':'flex','flexDirection':'row',
      'alignContent':'center','alignItems':'center',
      'justifyContent':'center','width':'fit-content',
      'border':'none'}}>
        <label style={{'margin':'5px'}}>Query by date:</label>
        <input ref={date} type='text'></input>
        <button onClick={()=>getDates(date.current.value)}>Submit</button>
      </fieldset>
      <fieldset style={{'display':'flex','flexDirection':'row',
      'alignContent':'center','alignItems':'center',
      'justifyContent':'center','width':'fit-content',
      'border':'none'}}>
        <label style={{'margin':'5px'}}>Query by Trade ID:</label>
        <input ref={trade} type='text'></input>
        <button onClick={()=>getTrades(trade.current.value)}>Submit</button>
      </fieldset>
      <fieldset style={{'display':'flex','flexDirection':'row',
      'alignContent':'center','alignItems':'center',
      'justifyContent':'center','width':'fit-content',
      'border':'none'}}>
        <label style={{'margin':'5px'}}>Query by Client ID:</label>
        <input ref={client} type='text'></input>
        <button onClick={()=>getClient(client.current.value)}>Submit</button>
      </fieldset>
      </fieldset>

      <div ref={resultsList} style={{'marginTop':'60px'}}>
      {received&&<div style={{'paddingLeft':'60px','paddingRight':'60px'}}>
      <p style={{'fontSize':'5vmin','margin':'1vmin','color':'green',
    'marginTop':'3.5vmin'}}>{choice}</p>

        {results.map(data=>(
        <div style={{'marginBottom':'20px'}}>
           <hr></hr>
        <p style={{'color':'blue','fontSize':'4vmin'}}>{data.client}</p>
        <p style={{'color':'blue'}}>ENTITY: </p>
        {data.docs.map(data=>(<div>
          <span>{data.entityId} </span></div>
        ))}
        <p style={{'color':'blue'}}>DOCS: </p>
        {data.docs.map((data)=>(
          <span>{data.documentId}</span>
        ))}
        
        <p style={{'color':'blue'}}>TRADES:</p>
        {data.trades.map((val,index)=>(
          index==data.trades.length-1?<span>{val}</span>:<span>{val}, </span>
        ))}
        <br></br>
       
       </div>
       ))}
      </div>}
      {exception && <div style={{'paddingLeft':'60px','paddingRight':'60px','marginTop':'0px','fontSize':'4vmin'}}><p style={{'fontSize':'5vmin','margin':'1vmin','color':'green',
    }}>No GTT breaks</p><hr></hr>{exception}</div>}

      </div>
    </div>
  );
}

export default App;
