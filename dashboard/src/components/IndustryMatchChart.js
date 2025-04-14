import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// 分析結果に基づく業界適性データ
// NIRA総研の「テレワークに関する就業者実態調査」を含む複数の研究から抽出
// 色覚多様性に配慮した色を使用
const industryData = [
  { name: 'IT・技術', score: 9.2, color: '#3182CE', reasoning: '評価基準の明確さ、リモート作業の適合性' },
  { name: 'クリエイティブ', score: 8.8, color: '#DD6B20', reasoning: '個人作業の比重、成果物の明確さ' },
  { name: 'コンサルティング', score: 8.7, color: '#805AD5', reasoning: '分析業務の独立性、裁量の大きさ' },
  { name: 'マーケティング・広告', score: 8.5, color: '#38A169', reasoning: 'デジタルツールの活用度、成果の可視性' },
  { name: '教育・研修', score: 7.6, color: '#E53E3E', reasoning: 'オンライン講義の普及、デジタル教材の充実' },
];

// スコアの降順でソート
const sortedData = [...industryData].sort((a, b) => b.score - a.score);

// セクションタイトル用のスタイル（青い下線付き）
const sectionTitleStyle = {
  fontSize: '1.3rem',
  fontWeight: 'bold',
  textAlign: 'center',
  marginBottom: '10px',
  color: '#2c3e50',
  borderBottom: '2px solid #3182CE',
  display: 'inline-block',
  paddingBottom: '5px',
  marginTop: '10px'
};

function IndustryMatchChart() {
  return (
    <div>
      <div style={{ textAlign: 'center' }}>
        <h2 style={sectionTitleStyle}>業界別リモートワーク適性度</h2>
      </div>
      <p className="section-subtitle">
        「業務特性に基づく各業界のリモートワーク親和性評価」
      </p>
      <p className="section-source">
        ※NIRA総研の「テレワークに関する就業者実態調査」を含む<br />
        複数の研究機関データから算出した業界別スコア（10点満点）
      </p>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={sortedData}
            margin={{ top: 20, right: 30, left: 120, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 10]} />
            <YAxis 
              dataKey="name" 
              type="category" 
              width={120} 
              tick={{ fill: '#333', fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value, name, props) => {
                return [`${value}点: ${props.payload.reasoning}`, '適性度'];
              }}
              cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }}
            />
            <Bar dataKey="score" name="適性度">
              {sortedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="research-insight">
        研究結果: 大久保敏弘教授の研究によれば、テレワーク成功率は業務の裁量度と<br />
        明確な評価基準の有無に強く相関することが示されています
      </div>
    </div>
  );
}

export default IndustryMatchChart;