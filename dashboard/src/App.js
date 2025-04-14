import React from 'react';
import './App.css';
import SkillsRadarChart from './components/SkillsRadarChart';
import IndustryMatchChart from './components/IndustryMatchChart';
import AchievementsTimeline from './components/AchievementsTimeline';
import ValuePropositionCards from './components/ValuePropositionCards';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>リモートワーク分析ダッシュボード</h1>
        <p className="data-source-header">
          NIRA総研の「テレワークに関する就業者実態調査」および大久保敏弘教授（慶應義塾大学）の研究に基づく分析
        </p>
      </header>
      <main>
        <section className="dashboard-section">
          <h2>総合サマリー</h2>
          <SkillsRadarChart />
        </section>
        
        <section className="dashboard-section">
          <h2>業界適性分析</h2>
          <IndustryMatchChart />
        </section>
        
        <section className="dashboard-section">
          <h2>実績とタイムライン</h2>
          <AchievementsTimeline />
        </section>
        
        <section className="dashboard-section">
          <h2>価値のご提案</h2>
          <ValuePropositionCards />
        </section>

        <div className="dashboard-footer">
          <p>© 2025 リモートワーク分析プロジェクト</p>
          <p className="data-source-footer">
            データソース: NIRA総合研究開発機構「テレワークに関する就業者実態調査」、大久保敏弘教授研究論文、および553件の関連記事分析
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;