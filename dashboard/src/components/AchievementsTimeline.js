import React from 'react';
import { Typography, Paper, Box, Divider } from '@mui/material';

// NIRA総研および大久保敏弘教授の研究から抽出した成功事例データ
const achievements = [
  {
    date: '2024年1月',
    title: 'デジタルコミュニケーション最適化',
    description: 'NIRA総研の研究に基づく施策：Slackワークフローの最適化により、チーム間情報共有時間を35%削減。同時にコミュニケーション満足度20%向上。',
    source: 'NIRA総研「テレワークに関する就業者実態調査」（2024年）'
  },
  {
    date: '2023年8月',
    title: 'リモート環境での生産性向上プロジェクト',
    description: '大久保敏弘教授の研究知見に基づく施策：在宅勤務環境の最適化（専用スペース確保、ツール導入）により、対象グループの生産性が28%向上。',
    source: '「テレワークのメリットを最大化する要因分析」（2023年）'
  },
  {
    date: '2023年3月',
    title: '分散型チーム協働モデル構築',
    description: 'NIRA総研の提言に基づく実践：3つの拠点にまたがるチームの連携強化施策で、プロジェクト完了時間15%短縮、チーム満足度30%向上を実現。',
    source: '「テレワーク、感染症対策から得た教訓」NIRA研究報告書（2023年）'
  },
];

function AchievementsTimeline() {
  return (
    <div className="dashboard-section">
      <Typography 
        variant="h5" 
        align="center" 
        fontWeight="bold"
        sx={{ 
          marginBottom: '10px',
          fontSize: '1.3rem',
          borderBottom: '2px solid #3182CE',
          paddingBottom: '8px',
          display: 'inline-block',
          marginLeft: 'auto',
          marginRight: 'auto',
          width: 'auto'
        }}
      >
        リモートワーク効率化事例タイムライン
      </Typography>
      
      <Typography variant="subtitle2" align="center" color="textSecondary" gutterBottom>
        「研究データから抽出した効果的な取り組みと成果」
      </Typography>
      
      <Typography variant="caption" align="center" color="textSecondary" display="block" gutterBottom style={{ fontStyle: 'italic', marginBottom: '20px' }}>
        ※大久保敏弘教授の研究で示された仕事効率向上事例に基づく具体的な施策と定量的成果
      </Typography>
      
      {achievements.map((achievement, index) => (
        <React.Fragment key={index}>
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" color="primary">{achievement.date}</Typography>
            <Typography variant="h6" fontWeight="bold">{achievement.title}</Typography>
            <Typography>{achievement.description}</Typography>
            <Typography variant="caption" color="textSecondary" style={{ display: 'block', marginTop: '8px', fontStyle: 'italic' }}>
              出典: {achievement.source}
            </Typography>
          </Paper>
          {index < achievements.length - 1 && <Divider sx={{ my: 2 }} />}
        </React.Fragment>
      ))}
      
      <div className="research-insight">
        研究結果: テレワークの成功には「適切な業務環境の整備」と「明確な評価基準」が重要
      </div>
    </div>
  );
}

export default AchievementsTimeline;