import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';

import uploadIcon from './assets/upload.png';
import logoIcon from './assets/logo.png';
import userIcon from './assets/user.png';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [currentData, setCurrentData] = useState(null);
  const [history, setHistory] = useState([]);

  // load history after login
  useEffect(() => {
    if (token) fetchHistory();
  }, [token]);

  const getHeaders = () => {
    return token ? { headers: { Authorization: `Token ${token}` } } : {};
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/login/', { username, password });
      const userToken = res.data.token;
      setToken(userToken);
      localStorage.setItem('token', userToken);
    } catch (err) { alert("Login Failed: Check credentials"); }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/history/', getHeaders());
      setHistory(res.data);
    } catch (err) { console.error(err); }
  };

  const loadHistoryItem = async (id) => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/history/${id}/`, getHeaders());
      setCurrentData(res.data); 
    } catch (err) { 
      console.error(err);
      alert("Could not load history item."); 
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, getHeaders());
      setCurrentData(res.data);
      fetchHistory();
    } catch (err) { alert("Upload failed"); }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    setCurrentData(null); 
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow-md w-96 flex flex-col items-center">
          <img src={logoIcon} alt="Logo" className="w-10 h-10 mb-2" />
          
          <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mb-4">
              <img src={userIcon} alt="User" className="w-8 h-8 opacity-80" />
          </div>
          
          <h2 className="text-2xl font-bold mb-6 text-slate-800">Welcome Back</h2>
          <input className="w-full p-3 mb-4 border rounded" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input className="w-full p-3 mb-6 border rounded" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          <button className="w-full bg-teal-600 text-white p-3 rounded font-bold hover:bg-teal-700">Sign In</button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-slate-50">
      <header className="w-full max-w-6xl flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
            <img src={logoIcon} alt="Logo" className="w-8 h-8" />
            <h1 className="text-3xl font-bold text-slate-800">Chemical Visualizer</h1>
        </div>
        <div className="flex gap-4">
          <label className="cursor-pointer bg-teal-600 hover:bg-teal-700 text-white font-semibold py-2 px-6 rounded shadow transition flex items-center gap-2">
            <img src={uploadIcon} alt="" className="w-5 h-5 invert brightness-0" style={{ filter: 'brightness(0) invert(1)' }} />
            Upload CSV
            <input type="file" className="hidden" onChange={handleFileUpload} accept=".csv"/>
          </label>
          <button onClick={handleLogout} className="text-slate-500 hover:text-red-500 font-semibold transition">Logout</button>
        </div>
      </header>

      <main className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1 bg-white p-4 rounded-xl shadow-sm h-fit">
          <h2 className="text-sm font-bold text-slate-400 uppercase mb-4 tracking-wider">History</h2>
          <div className="space-y-3">
            {history.map((item) => (
              <div 
                key={item.id} 
                onClick={() => loadHistoryItem(item.id)}
                className="p-3 border rounded hover:bg-teal-50 hover:border-teal-200 cursor-pointer transition-colors text-sm group"
              >
                <div className="font-semibold text-slate-700 group-hover:text-teal-700">Dataset #{item.id}</div>
                <div className="text-xs text-slate-500">{new Date(item.uploaded_at).toLocaleTimeString()}</div>
                <div className="text-xs text-slate-400 mt-1">
                    {item.total_records} units • {item.avg_pressure.toFixed(1)} Bar
                </div>
              </div>
            ))}
            {history.length === 0 && <div className="text-slate-400 text-sm italic">No history yet.</div>}
          </div>
        </div>

        <div className="md:col-span-3">
          <Dashboard data={currentData} />
        </div>
      </main>
    </div>
  );
}

export default App;