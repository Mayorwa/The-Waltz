import './App.css'
import GoalVisualization from './components/GoalVisualization'
import Legend from './components/Legend'
import { matchInfo } from './data/goalData'

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="title-section">
          <h1>{matchInfo.homeTeam}</h1>
          <p className="match-subtitle">v {matchInfo.awayTeam} {matchInfo.year}</p>
        </div>
        <Legend />
      </header>

      <p className="goal-info">{matchInfo.goalInfo}</p>

      <main className="main">
        <GoalVisualization />
      </main>

      <footer className="footer">
        ongoalsscored.com
      </footer>
    </div>
  )
}

export default App
