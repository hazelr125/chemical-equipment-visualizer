import React, { useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

import pdfIcon from '../assets/pdf.png';
import searchIcon from '../assets/search.png';
import pressureIcon from '../assets/pressure.png';
import tempIcon from '../assets/temperature.png';
import unitsIcon from '../assets/units.png';
import chartIcon from '../assets/chart.png';
import listIcon from '../assets/list.png';

ChartJS.register(ArcElement, Tooltip, Legend);

const Dashboard = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');

  if (!data) return (
    <div className="bg-white p-12 rounded-xl shadow-sm text-center border border-dashed border-slate-300">
      <div className="text-slate-400 text-lg mb-2">No Data Available</div>
      <p className="text-sm text-slate-500">Upload a CSV file to view analysis and generate reports.</p>
    </div>
  );

  const { stats, data: rows, history_id } = data;

  const filteredRows = rows ? rows.filter(row => 
    row['Equipment Name'].toLowerCase().includes(searchTerm.toLowerCase()) ||
    row['Type'].toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const chartData = {
    labels: Object.keys(stats.type_distribution),
    datasets: [{
      data: Object.values(stats.type_distribution),
      backgroundColor: ['#0F766E', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6'],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };

  const handleDownloadReport = () => {
    if (history_id) {
      window.open(`http://127.0.0.1:8000/api/report/${history_id}/`, '_blank');
    } else {
      alert("No report ID found. Please upload a file again.");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <h2 className="text-lg font-bold text-slate-700">Analysis Results</h2>
        <button 
          onClick={handleDownloadReport}
          className="bg-slate-800 hover:bg-slate-900 text-white text-sm font-semibold py-2 px-4 rounded shadow transition flex items-center gap-2"
        >
          <img src={pdfIcon} alt="" className="w-4 h-4 invert brightness-0" style={{ filter: 'brightness(0) invert(1)' }}/>
          Download PDF Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Total Units" value={stats.total_records} icon={unitsIcon} color="border-l-teal-600" />
        <StatCard label="Avg Pressure" value={stats.avg_pressure} unit="Bar" icon={pressureIcon} color="border-l-amber-500" />
        <StatCard label="Avg Temp" value={stats.avg_temp} unit="°C" icon={tempIcon} color="border-l-blue-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <img src={chartIcon} alt="" className="w-5 h-5 opacity-60"/>
            <h3 className="font-bold text-slate-700 text-sm uppercase tracking-wide">Equipment Distribution</h3>
          </div>
          <div className="h-64 flex justify-center items-center">
            <Doughnut 
              data={chartData} 
              options={{ 
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'right', labels: { usePointStyle: true, boxWidth: 8 } }
                }
              }} 
            />
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col h-[400px]">
          
          <div className="flex justify-between items-center mb-4 shrink-0">
            <div className="flex items-center gap-2">
                <img src={listIcon} alt="" className="w-5 h-5 opacity-60"/>
                <h3 className="font-bold text-slate-700 text-sm uppercase tracking-wide">Live Data Feed</h3>
            </div>
            
            <div className="relative">
                <img src={searchIcon} alt="" className="w-4 h-4 absolute left-3 top-2.5 opacity-40" />
                <input 
                  type="text" 
                  placeholder="Search..." 
                  className="border border-slate-300 pl-10 pr-4 py-2 rounded text-sm w-40 focus:ring-2 focus:ring-teal-500 outline-none transition"
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
          </div>

          <div className="overflow-y-auto border rounded scrollbar-thin scrollbar-thumb-slate-200 grow">
            <table className="w-full text-sm text-left text-slate-600 table-fixed">
              <thead className="bg-slate-50 text-xs uppercase font-bold sticky top-0 z-10 text-slate-500 shadow-sm">
                <tr>
                  <th className="w-[50%] px-4 py-3 border-b bg-slate-50">Name</th>
                  <th className="w-[30%] px-4 py-3 border-b bg-slate-50">Type</th>
                  <th className="w-[20%] px-4 py-3 border-b text-right bg-slate-50">Flow</th>
                </tr>
              </thead>
              
              <tbody className="divide-y divide-slate-100">
                {filteredRows.map((row, i) => {
                  const isCritical = (row['Pressure'] > 8.0 || row['Temperature'] > 100);

                  return (
                    <tr 
                      key={i} 
                      className={`transition-colors border-l-4 ${
                        isCritical 
                          ? 'bg-red-50 border-red-500 hover:bg-red-100' 
                          : 'border-transparent hover:bg-slate-50'
                      }`}
                    >
                      <td className="px-4 py-3 font-medium text-slate-800 break-words align-top">
                        <div className="flex flex-col gap-1">
                          <span>{row['Equipment Name']}</span>
                          {isCritical && (
                            <span className="w-fit px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-600 border border-red-200 uppercase tracking-wide">
                              ⚠ Critical
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs align-top">
                        <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-600 font-semibold border border-slate-200 inline-block">
                          {row['Type']}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-slate-600 align-top">
                        {row['Flowrate']}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, unit, color, icon }) => (
  <div className={`bg-white p-5 rounded-xl shadow-sm border-l-4 ${color} flex items-center justify-between`}>
    <div>
      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <p className="text-3xl font-bold text-slate-800">{value}</p>
        {unit && <span className="text-sm font-medium text-slate-500">{unit}</span>}
      </div>
    </div>
    <img src={icon} alt={label} className="w-10 h-10 opacity-10 grayscale" />
  </div>
);

export default Dashboard;