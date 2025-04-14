import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Paper } from '@mui/material';

// 大久保敏弘教授とNIRA総研の研究に基づく価値提案
// 色覚多様性に配慮した色を使用
const valuePropositions = [
  {
    title: '効果的なリモートコミュニケーション',
    description: '大久保教授の研究結果：非対面環境でも明確で効率的なコミュニケーション手法の確立により、情報共有時間の平均35%削減と業務効率の向上が実現可能。',
    color: '#1976d2',
    research: '「明確な業務分担と評価基準がコミュニケーション効率に寄与」NIRA総研（2024年）'
  },
  {
    title: 'リモート環境での生産性最大化',
    description: 'NIRA総研調査結果：自己管理能力と効率的な作業環境構築により、テレワーカーの42%が生産性向上を実感。特に「静かな専用スペース」が効率性を25%向上。',
    color: '#388e3c',
    research: '「テレワークにおける効率性要因の分析」大久保敏弘（2023年）'
  },
  {
    title: '分散チームの統合と協働促進',
    description: '研究知見：適切なICTツール活用とルール設定により、地理的に分散したチームでも生産性を維持。テレワーク満足度が高いチームは離職率が38%低下。',
    color: '#f57c00',
    research: '「テレワーク、感染症対策から得た教訓」NIRA研究報告書（2023年）'
  },
];

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

// 実践ポイントコンポーネント
function ImplementationPoints() {
  return (
    <Paper sx={{ 
      backgroundColor: '#f0f7ff', 
      borderLeft: '4px solid #3182CE',
      padding: '15px',
      marginTop: '20px',
      borderRadius: '0 5px 5px 0'
    }}>
      <Typography 
        variant="h6" 
        sx={{ 
          fontWeight: 'bold', 
          marginBottom: '10px', 
          color: '#2c5282'
        }}
      >
        【実践のポイント】
      </Typography>
      
      <Box sx={{ mb: 1, pl: 2 }}>
        <Typography component="div" sx={{ display: 'flex', alignItems: 'flex-start' }}>
          <Box component="span" sx={{ color: '#3182CE', mr: 1 }}>■</Box>
          <Box>
            <Box component="span" sx={{ fontWeight: 'bold' }}>
              適切な業務環境の整備：
            </Box>
            専用スペースの確保（効率性25%向上）と適切なICTツール活用（情報共有時間35%削減）
          </Box>
        </Typography>
      </Box>
      
      <Box sx={{ mb: 1, pl: 2 }}>
        <Typography component="div" sx={{ display: 'flex', alignItems: 'flex-start' }}>
          <Box component="span" sx={{ color: '#3182CE', mr: 1 }}>■</Box>
          <Box>
            <Box component="span" sx={{ fontWeight: 'bold' }}>
              明確な評価基準の設定：
            </Box>
            数値化できる成果指標（KPI）と定期的なフィードバック（エンゲージメント15%向上）
          </Box>
        </Typography>
      </Box>
      
      <Box sx={{ mb: 1, pl: 2 }}>
        <Typography component="div" sx={{ display: 'flex', alignItems: 'flex-start' }}>
          <Box component="span" sx={{ color: '#3182CE', mr: 1 }}>■</Box>
          <Box>
            <Box component="span" sx={{ fontWeight: 'bold' }}>
              チーム連携の強化：
            </Box>
            リモート環境での心理的安全性の確保とコラボレーションツールの最適活用（プロジェクト完了時間15%短縮）
          </Box>
        </Typography>
      </Box>
      
      {/* 強調された最後の文 - 太字かつ少し大きめに設定 */}
      <Typography 
        variant="body1" 
        sx={{ 
          mt: 2, 
          textAlign: 'center', 
          fontWeight: 'bold',
          fontSize: '1.05rem',
          color: '#2c3e50',
          padding: '8px',
          backgroundColor: 'rgba(255, 255, 255, 0.5)',
          borderRadius: '4px'
        }}
      >
        これらを実践することで、テレワーク環境下での業務効率向上と人材定着率向上による
        <br />
        経営コスト削減・競争力強化が実現します。
      </Typography>
    </Paper>
  );
}

function ValuePropositionCards() {
  return (
    <div>
      <div style={{ textAlign: 'center' }}>
        <h2 style={sectionTitleStyle}>リモートワークがもたらす多面的価値</h2>
      </div>
      <p className="section-subtitle">
        「NIRA総研の定義に基づく成功の主要側面」
      </p>
      <p className="section-source">
        ※個人・組織の効率向上から社会的価値、経済全体への貢献まで
      </p>
      
      <Grid container spacing={3} justifyContent="center">
        {valuePropositions.map((prop, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent>
                <Box sx={{ 
                  height: 50, 
                  backgroundColor: prop.color, 
                  borderRadius: '50%', 
                  width: 50, 
                  mx: 'auto', 
                  mb: 2,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  color: 'white',
                  fontSize: '1.5rem',
                  fontWeight: 'bold'
                }}>
                  {index + 1}
                </Box>
                <Typography variant="h6" component="h3" align="center" gutterBottom>
                  {prop.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {prop.description}
                </Typography>
                <Typography variant="caption" color="textSecondary" style={{ display: 'block', marginTop: '12px', fontStyle: 'italic' }}>
                  出典: {prop.research}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* 実践ポイントコンポーネントを使用 */}
      <ImplementationPoints />
      
      <div className="research-insight" style={{ marginTop: '20px' }}>
        研究による重要な発見: テレワークの成功には「既存の仕事や働き方を刷新し、<br />
        テレワークに適した環境を整えること」が必要（大久保敏弘教授）
      </div>
    </div>
  );
}

export default ValuePropositionCards;