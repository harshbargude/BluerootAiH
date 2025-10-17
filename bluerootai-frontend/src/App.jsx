import React from 'react';
import '/src/App.css'
import RealtimeCharts from './components/RealtimeCharts.jsx'
import Controls from './components/Controls.jsx'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">BlueRoot AI - Water Quality Dashboard</h1>
        </header>
        <Controls />
        <RealtimeCharts />
      </div>
    </div>
  )
}

export default App
