import React from 'react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

// リモートワーク成功要因に基づくデータ
// NIRA総研調査および大久保敏弘教授の研究から抽出
// 色覚多様性に配慮した色を使用
const data = [
  {
    subject: 'コミュニケーション力',
    value: 85,
    fullMark: 100,
  },
  {
    subject: '自己管理能力',
    value: 90,
    fullMark: 100,
  },
  {
    subject: 'デジタルリテラシー',
    value: 80,
    fullMark: 100,
  },
  {
    subject: 'タスク管理能力',
    value: 75,
    fullMark: 100,
  },
  {
    subject: '問題解決能力',
    value: 85,
    fullMark: 100,
  },
  {
    subject: '成果志向性',
    value: 88,
    fullMark: 100,
  },
];

// 専用スペースの定義
const specializedSpaceDefinition = 
  "大久保敏弘教授の研究における「静かな専用スペース」とは、テレワーク専用の区切られた作業空間で、" +
  "仕事に集中できる静穏な環境が確保され、業務に必要な機器・設備が整った場所を指します。" +
  "具体的には、書斎・専用の部屋（最も効率向上との相関が高い）、パーティションで区切られた専用コーナー、" +
  "サテライトオフィスなどが含まれます。研究では、専用スペースの確保により平均25%の効率性向上が確認されています。";

// 評価基準の定義
const evaluationCriteriaDefinition = 
  "大久保敏弘教授の研究における「明確な評価基準」とは、従業員の業績や成果に対して、具体的で透明性のある" +
  "基準に基づいて評価を行うことです。例えば、KPI（重要業績評価指標）の明示、定期的なフィードバックの実施、" +
  "評価基準の公開、チーム業績と個人業績の両立などが含まれます。研究では、評価基準が明確な企業では従業員の" +
  "エンゲージメントが約15%向上することが示されています。";

function SkillsRadarChart() {
  return (
    <div>
      <h2 className="section-title">リモートワーク成功要因スキル分析</h2>
      <p className="section-subtitle">
        「NIRA総研調査および国内外の研究データに基づく主要成功要因」
      </p>
      <p className="section-source">
        ※553件の関連記事と大久保敏弘教授（慶應義塾大学）の研究から抽出した<br />
        リモートワーク環境で効率向上に寄与する重要スキル
      </p>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart 
            cx="50%" 
            cy="50%" 
            outerRadius="80%" 
            data={data}
            margin={{ top: 0, right: 30, bottom: 0, left: 30 }}
          >
            <PolarGrid />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: '#333', fontSize: 12 }}
              dy={4} // テキストをグラフの外側に少し移動
            />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar
              name="スキルレベル"
              dataKey="value"
              stroke="#4F46E5" // 色覚多様性に配慮した青紫
              fill="#4F46E5"
              fillOpacity={0.6}
            />
            <Tooltip formatter={(value) => [`${value}点`, 'スキル重要度']} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="research-insight">
        研究結果: テレワークで効率が上がるのは、仕事の評価基準が明確で、<br />
        リモートでできる仕事が多く、裁量が大きい業務であることが明らかになっています
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '15px', fontSize: '0.8rem' }}>
        <div className="tooltip-container">
          <span className="tooltip-text">「静かな専用スペース」の定義</span>
          <div className="tooltip-content">{specializedSpaceDefinition}</div>
        </div>
        <div className="tooltip-container">
          <span className="tooltip-text">「明確な評価基準」の定義</span>
          <div className="tooltip-content">{evaluationCriteriaDefinition}</div>
        </div>
      </div>
    </div>
  );
}

export default SkillsRadarChart;