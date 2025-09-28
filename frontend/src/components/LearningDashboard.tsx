"use client"

import React, { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Stack,
  Avatar,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  School as SchoolIcon,
  Star as StarIcon,
  MenuBook as BookOpenIcon,
  GpsFixed as TargetIcon,
  Chat as ChatIcon,
  Code as CodeIcon,
  SmartToy as RobotIcon,
  LocalFireDepartment as FireIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface Skill {
  name: string
  level: number
  maxLevel: number
  progress: number
}

interface Achievement {
  id: string
  title: string
  description: string
  earned: boolean
  icon: string
}

export function LearningDashboard() {
  const [skills] = useState<Skill[]>([
    { name: 'JavaScript', level: 3, maxLevel: 5, progress: 60 },
    { name: 'React', level: 2, maxLevel: 5, progress: 40 },
    { name: 'AI Collaboration', level: 1, maxLevel: 5, progress: 20 },
    { name: 'Problem Solving', level: 4, maxLevel: 5, progress: 80 },
  ])

  const [achievements] = useState<Achievement[]>([
    { id: '1', title: 'First Chat', description: 'Had your first conversation with AI', earned: true, icon: '💬' },
    { id: '2', title: 'Code Explorer', description: 'Wrote your first code with AI assistance', earned: true, icon: '💻' },
    { id: '3', title: 'Multi-Model Master', description: 'Used 3 different AI models', earned: false, icon: '🤖' },
    { id: '4', title: 'Learning Streak', description: '7 days of continuous learning', earned: false, icon: '🔥' },
  ])

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, height: '100%', overflow: 'auto' }}>
      <Typography 
        variant="h4" 
        gutterBottom 
        sx={{ 
          background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 700,
          mb: 3
        }}
      >
        📊 Learning Hub
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Track your progress and achievements in your personal AI learning journey
      </Typography>

      {/* Progress Overview Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card 
          sx={{ 
            mb: 3,
            background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
            color: 'white'
          }}
        >
          <CardContent>
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Today's Progress
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Keep up the great work!
                </Typography>
              </Box>
              <TrendingUpIcon sx={{ fontSize: 32 }} />
            </Stack>
            
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <div style={{ width: '100%', padding: '8px' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    12
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.75 }}>
                    Messages
                  </Typography>
                </Box>
              </div>
              <div style={{ width: '100%', padding: '8px' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    3
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.75 }}>
                    Code Files
                  </Typography>
                </Box>
              </div>
              <div style={{ width: '100%', padding: '8px' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    45m
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.75 }}>
                    Learning Time
                  </Typography>
                </Box>
              </div>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Skills Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
              <TargetIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Skills
              </Typography>
            </Stack>
            
            <Stack spacing={2}>
              {skills.map((skill, index) => (
                <Box key={index}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {skill.name}
                    </Typography>
                    <Chip 
                      label={`Level ${skill.level}/${skill.maxLevel}`} 
                      size="small" 
                      color="primary"
                      variant="outlined"
                    />
                  </Stack>
                  <LinearProgress 
                    variant="determinate" 
                    value={skill.progress} 
                    sx={{ 
                      height: 8, 
                      borderRadius: 4,
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                      }
                    }}
                  />
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </motion.div>

      {/* Achievements Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
              <TrophyIcon color="secondary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Achievements
              </Typography>
            </Stack>
            
            <Grid container spacing={2}>
              {achievements.map((achievement) => (
                <div key={achievement.id} style={{ width: '100%', padding: '8px' }}>
                  <Card 
                    sx={{ 
                      opacity: achievement.earned ? 1 : 0.6,
                      background: achievement.earned 
                        ? 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)'
                        : 'transparent',
                      border: achievement.earned 
                        ? '1px solid rgba(156, 39, 176, 0.3)' 
                        : '1px solid rgba(0,0,0,0.12)'
                    }}
                  >
                    <CardContent>
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <Avatar sx={{ bgcolor: 'transparent', fontSize: '1.5rem' }}>
                          {achievement.icon}
                        </Avatar>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              fontWeight: 500,
                              color: achievement.earned ? 'text.primary' : 'text.secondary'
                            }}
                          >
                            {achievement.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {achievement.description}
                          </Typography>
                        </Box>
                        {achievement.earned && (
                          <StarIcon color="secondary" />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommended Learning */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
              <BookOpenIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Recommended
              </Typography>
            </Stack>
            
            <Card 
              sx={{ 
                background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
                border: '1px solid rgba(25, 118, 210, 0.2)'
              }}
            >
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={3}>
                  <Avatar 
                    sx={{ 
                      bgcolor: 'primary.main',
                      width: 48,
                      height: 48
                    }}
                  >
                    <TargetIcon />
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500, mb: 0.5 }}>
                      Next Learning Goal
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Complete 5 more coding challenges to level up your JavaScript skills
                    </Typography>
                  </Box>
                  <Chip 
                    label="Start Learning" 
                    color="primary" 
                    variant="filled"
                    sx={{ cursor: 'pointer', '&:hover': { opacity: 0.8 } }}
                  />
                </Stack>
              </CardContent>
            </Card>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  )
}