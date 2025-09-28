'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Grid,
  Avatar,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Tabs,
  Tab,
  Badge
} from '@mui/material'
import {
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  ThumbDown as ThumbDownIcon,
  ThumbUp as ThumbUpIcon,
  Chat as ChatIcon,
  Gavel as GavelIcon,
  Balance as BalanceIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
  Help as HelpIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Insights as InsightsIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface DebateArgument {
  id: string
  agentId: string
  agentName: string
  position: 'pro' | 'con'
  argument: string
  confidence: number
  evidence: string[]
  timestamp: Date
  votes: { up: number; down: number }
  rebuttals: Rebuttal[]
}

interface Rebuttal {
  id: string
  agentId: string
  agentName: string
  counterArgument: string
  timestamp: Date
  strength: number
}

interface Agent {
  id: string
  name: string
  role: string
  personality: string
  expertise: string[]
  bias: 'conservative' | 'liberal' | 'neutral' | 'skeptical' | 'optimistic'
  avatar: string
  isActive: boolean
  totalArguments: number
  winRate: number
  averageConfidence: number
}

const agents: Agent[] = [
  {
    id: 'devil',
    name: 'Devil\'s Advocate',
    role: 'Skeptical Challenger',
    personality: 'Always questions assumptions, finds flaws in arguments, plays devil\'s advocate',
    expertise: ['Critical Thinking', 'Logical Fallacies', 'Risk Assessment', 'Counter-Arguments'],
    bias: 'skeptical',
    avatar: '🎭',
    isActive: true,
    totalArguments: 0,
    winRate: 0,
    averageConfidence: 0
  },
  {
    id: 'optimist',
    name: 'Optimistic Analyst',
    role: 'Positive Supporter',
    personality: 'Finds benefits, sees opportunities, supports innovative ideas',
    expertise: ['Opportunity Analysis', 'Benefit Assessment', 'Innovation Support', 'Positive Thinking'],
    bias: 'optimistic',
    avatar: '🌟',
    isActive: true,
    totalArguments: 0,
    winRate: 0,
    averageConfidence: 0
  },
  {
    id: 'conservative',
    name: 'Conservative Evaluator',
    role: 'Risk-Averse Advisor',
    personality: 'Cautious, prefers proven solutions, emphasizes stability and security',
    expertise: ['Risk Management', 'Stability Analysis', 'Security Assessment', 'Proven Solutions'],
    bias: 'conservative',
    avatar: '🛡️',
    isActive: true,
    totalArguments: 0,
    winRate: 0,
    averageConfidence: 0
  },
  {
    id: 'liberal',
    name: 'Liberal Innovator',
    role: 'Progressive Thinker',
    personality: 'Embraces change, supports innovation, challenges traditional approaches',
    expertise: ['Innovation Strategy', 'Change Management', 'Progressive Thinking', 'Future Planning'],
    bias: 'liberal',
    avatar: '🚀',
    isActive: true,
    totalArguments: 0,
    winRate: 0,
    averageConfidence: 0
  },
  {
    id: 'neutral',
    name: 'Neutral Arbiter',
    role: 'Balanced Mediator',
    personality: 'Objective, data-driven, provides balanced analysis without bias',
    expertise: ['Data Analysis', 'Objective Assessment', 'Mediation', 'Balanced Evaluation'],
    bias: 'neutral',
    avatar: '⚖️',
    isActive: true,
    totalArguments: 0,
    winRate: 0,
    averageConfidence: 0
  }
]

const debateTopics = [
  'Should AI replace human decision-making?',
  'Is remote work more productive than office work?',
  'Should we prioritize speed or quality in development?',
  'Is open source better than proprietary software?',
  'Should we use microservices or monoliths?',
  'Is AI safety more important than AI capabilities?',
  'Should we optimize for user experience or developer experience?',
  'Is technical debt always bad?'
]

export default function DevilsAdvocateAgent() {
  const [activeTab, setActiveTab] = useState(0)
  const [debateArguments, setDebateArguments] = useState<DebateArgument[]>([])
  const [selectedTopic, setSelectedTopic] = useState('')
  const [isDebating, setIsDebating] = useState(false)
  const [debateSettings, setDebateSettings] = useState({
    maxArguments: 10,
    timeLimit: 300, // 5 minutes
    allowRebuttals: true,
    requireEvidence: true,
    minConfidence: 0.6
  })
  const [agentStats, setAgentStats] = useState<Agent[]>(agents)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  const startDebate = async () => {
    if (!selectedTopic) return
    
    setIsDebating(true)
    setDebateArguments([])
    
    // Simulate AI agents debating
    const debatePromises = agents
      .filter(agent => agent.isActive)
      .map(async (agent, index) => {
        await new Promise(resolve => setTimeout(resolve, index * 1000))
        
        const position = Math.random() > 0.5 ? 'pro' : 'con'
        const confidence = Math.random() * 0.4 + 0.6 // 0.6-1.0
        const argument = generateArgument(agent, selectedTopic, position)
        const evidence = generateEvidence(agent, selectedTopic)
        
        const newArgument: DebateArgument = {
          id: `arg-${Date.now()}-${agent.id}`,
          agentId: agent.id,
          agentName: agent.name,
          position,
          argument,
          confidence,
          evidence,
          timestamp: new Date(),
          votes: { up: 0, down: 0 },
          rebuttals: []
        }
        
        setDebateArguments(prev => [...prev, newArgument])
        
        // Update agent stats
        setAgentStats(prev => prev.map(a => 
          a.id === agent.id 
            ? { ...a, totalArguments: a.totalArguments + 1 }
            : a
        ))
      })
    
    await Promise.all(debatePromises)
    setIsDebating(false)
  }

  const generateArgument = (agent: Agent, topic: string, position: 'pro' | 'con'): string => {
    const templates = {
      devil: {
        pro: `As a skeptic, I must challenge the assumption that ${topic.toLowerCase()}. While there are benefits, we must consider the hidden risks and unintended consequences.`,
        con: `I'm playing devil's advocate here, but ${topic.toLowerCase()} has significant flaws that are often overlooked. The risks outweigh the benefits.`
      },
      optimist: {
        pro: `I'm excited about ${topic.toLowerCase()}! The opportunities are tremendous and the benefits far outweigh any concerns.`,
        con: `Even though I'm optimistic, I must acknowledge that ${topic.toLowerCase()} has some challenges that need addressing.`
      },
      conservative: {
        pro: `While ${topic.toLowerCase()} has merit, we should proceed cautiously and ensure all risks are mitigated.`,
        con: `${topic.toLowerCase()} introduces too many unknowns and risks. We should stick with proven approaches.`
      },
      liberal: {
        pro: `${topic.toLowerCase()} represents progress and innovation. We should embrace change and move forward boldly.`,
        con: `Even as a progressive thinker, I see that ${topic.toLowerCase()} might not be the right approach for this situation.`
      },
      neutral: {
        pro: `Based on the data, ${topic.toLowerCase()} shows measurable benefits that justify consideration.`,
        con: `The evidence suggests that ${topic.toLowerCase()} may not be the optimal solution based on current metrics.`
      },
      skeptical: {
        pro: `While I'm naturally skeptical, the evidence for ${topic.toLowerCase()} is compelling enough to warrant serious consideration.`,
        con: `I remain skeptical about ${topic.toLowerCase()} - the claims seem too good to be true and lack sufficient evidence.`
      },
      optimistic: {
        pro: `I'm optimistic about ${topic.toLowerCase()} - it has great potential and could lead to significant improvements.`,
        con: `Even as an optimist, I have concerns about ${topic.toLowerCase()} - we need to be realistic about the challenges.`
      }
    }
    
    return templates[agent.bias]?.[position] || `Agent ${agent.name} argues ${position === 'pro' ? 'for' : 'against'} ${topic.toLowerCase()}.`
  }

  const generateEvidence = (agent: Agent, topic: string): string[] => {
    const evidenceTypes = [
      'Research studies',
      'Industry reports',
      'Expert opinions',
      'Case studies',
      'Statistical data',
      'User feedback',
      'Performance metrics',
      'Risk assessments'
    ]
    
    return evidenceTypes
      .sort(() => Math.random() - 0.5)
      .slice(0, Math.floor(Math.random() * 3) + 2)
  }

  const addRebuttal = (argumentId: string, agentId: string) => {
    const agent = agents.find(a => a.id === agentId)
    if (!agent) return
    
    const rebuttal: Rebuttal = {
      id: `rebuttal-${Date.now()}`,
      agentId: agent.id,
      agentName: agent.name,
      counterArgument: `Agent ${agent.name} provides a counter-argument: "I disagree with this point because..."`,
      timestamp: new Date(),
      strength: Math.random() * 0.4 + 0.6
    }
    
    setDebateArguments(prev => prev.map(arg => 
      arg.id === argumentId 
        ? { ...arg, rebuttals: [...arg.rebuttals, rebuttal] }
        : arg
    ))
  }

  const voteOnArgument = (argumentId: string, vote: 'up' | 'down') => {
    setDebateArguments(prev => prev.map(arg => 
      arg.id === argumentId 
        ? { ...arg, votes: { ...arg.votes, [vote]: arg.votes[vote] + 1 } }
        : arg
    ))
  }

  const getAgentColor = (bias: string) => {
    const colors = {
      skeptical: 'error',
      optimistic: 'success',
      conservative: 'warning',
      liberal: 'info',
      neutral: 'default'
    }
    return colors[bias as keyof typeof colors] || 'default'
  }

  const getPositionIcon = (position: 'pro' | 'con') => {
    return position === 'pro' ? <TrendingUpIcon /> : <TrendingDownIcon />
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, height: '100%', overflow: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ 
          background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 'bold',
          mb: 1
        }}>
          🎭 Devil&apos;s Advocate AI Agents
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI agents that challenge each other, provide counter-arguments, and debate topics from multiple perspectives
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Debate Arena" icon={<GavelIcon />} />
          <Tab label="Agent Profiles" icon={<PsychologyIcon />} />
          <Tab label="Analytics" icon={<AssessmentIcon />} />
          <Tab label="Settings" icon={<SettingsIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          {/* Debate Controls */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Start a Debate</Typography>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
                <div style={{ flex: '1 1 300px', minWidth: '300px' }}>
                  <FormControl fullWidth>
                    <InputLabel>Select Debate Topic</InputLabel>
                    <Select
                      value={selectedTopic}
                      onChange={(e) => setSelectedTopic(e.target.value)}
                      label="Select Debate Topic"
                    >
                      {debateTopics.map((topic) => (
                        <MenuItem key={topic} value={topic}>{topic}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </div>
                <div style={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Button
                    variant="contained"
                    startIcon={isDebating ? <StopIcon /> : <PlayArrowIcon />}
                    onClick={isDebating ? () => setIsDebating(false) : startDebate}
                    disabled={!selectedTopic || isDebating}
                    fullWidth
                    sx={{ height: '56px' }}
                  >
                    {isDebating ? 'Stop Debate' : 'Start Debate'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Active Agents */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Active Agents</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {agents.filter(agent => agent.isActive).map((agent) => (
                  <Chip
                    key={agent.id}
                    avatar={<Avatar sx={{ bgcolor: `${getAgentColor(agent.bias)}.main` }}>{agent.avatar}</Avatar>}
                    label={agent.name}
                    color={getAgentColor(agent.bias) as any}
                    variant="outlined"
                  />
                ))}
              </Stack>
            </CardContent>
          </Card>

          {/* Debate Arguments */}
          <AnimatePresence>
            {debateArguments.map((argument, index) => (
              <motion.div
                key={argument.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: `${getAgentColor(agents.find(a => a.id === argument.agentId)?.bias || 'neutral')}.main`, mr: 2 }}>
                        {agents.find(a => a.id === argument.agentId)?.avatar}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                          {argument.agentName}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {agents.find(a => a.id === argument.agentId)?.role}
                        </Typography>
                      </Box>
                      <Chip
                        icon={getPositionIcon(argument.position)}
                        label={argument.position.toUpperCase()}
                        color={argument.position === 'pro' ? 'success' : 'error'}
                        variant="outlined"
                        sx={{ mr: 2 }}
                      />
                      <Chip
                        label={`${Math.round(argument.confidence * 100)}%`}
                        color={argument.confidence > 0.8 ? 'success' : argument.confidence > 0.6 ? 'warning' : 'error'}
                        variant="outlined"
                      />
                    </Box>

                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {argument.argument}
                    </Typography>

                    {/* Evidence */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Evidence:</Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        {argument.evidence.map((item, idx) => (
                          <Chip key={idx} label={item} size="small" variant="outlined" />
                        ))}
                      </Stack>
                    </Box>

                    {/* Actions */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Button
                        startIcon={<ThumbUpIcon />}
                        onClick={() => voteOnArgument(argument.id, 'up')}
                        size="small"
                        color="success"
                      >
                        {argument.votes.up}
                      </Button>
                      <Button
                        startIcon={<ThumbDownIcon />}
                        onClick={() => voteOnArgument(argument.id, 'down')}
                        size="small"
                        color="error"
                      >
                        {argument.votes.down}
                      </Button>
                      <Button
                        startIcon={<ChatIcon />}
                        onClick={() => addRebuttal(argument.id, 'devil')}
                        size="small"
                        color="primary"
                      >
                        Rebuttal
                      </Button>
                    </Box>

                    {/* Rebuttals */}
                    {argument.rebuttals.length > 0 && (
                      <Box sx={{ mt: 2, pl: 2, borderLeft: 2, borderColor: 'divider' }}>
                        <Typography variant="subtitle2" sx={{ mb: 1 }}>Rebuttals:</Typography>
                        {argument.rebuttals.map((rebuttal) => (
                          <Box key={rebuttal.id} sx={{ mb: 1, p: 1, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
                            <Typography variant="body2">
                              <strong>{rebuttal.agentName}:</strong> {rebuttal.counterArgument}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>Agent Profiles</Typography>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
            {agents.map((agent) => (
              <div key={agent.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 }
                  }}
                  onClick={() => setSelectedAgent(agent)}
                >
                  <CardContent>
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: `${getAgentColor(agent.bias)}.main`, mx: 'auto', mb: 1, width: 64, height: 64 }}>
                        {agent.avatar}
                      </Avatar>
                      <Typography variant="h6">{agent.name}</Typography>
                      <Typography variant="body2" color="text.secondary">{agent.role}</Typography>
                    </Box>
                    
                    <Typography variant="body2" sx={{ mb: 2 }}>{agent.personality}</Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Expertise:</Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        {agent.expertise.map((skill) => (
                          <Chip key={skill} label={skill} size="small" variant="outlined" />
                        ))}
                      </Stack>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Arguments:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{agent.totalArguments}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Win Rate:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{agent.winRate}%</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Avg Confidence:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{agent.averageConfidence}%</Typography>
                    </Box>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>Debate Analytics</Typography>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
            <div>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Agent Performance</Typography>
                  <Stack spacing={2}>
                    {agents.map((agent) => (
                      <Box key={agent.id} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: `${getAgentColor(agent.bias)}.main` }}>
                          {agent.avatar}
                        </Avatar>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle2">{agent.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {agent.totalArguments} arguments • {agent.winRate}% win rate
                          </Typography>
                        </Box>
                        <CircularProgress
                          variant="determinate"
                          value={agent.averageConfidence}
                          size={40}
                          thickness={4}
                        />
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </div>
            
            <div>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Debate Statistics</Typography>
                  <Stack spacing={2}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Arguments:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {debateArguments.length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Pro Arguments:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {debateArguments.filter(a => a.position === 'pro').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Con Arguments:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {debateArguments.filter(a => a.position === 'con').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Rebuttals:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {debateArguments.reduce((sum, arg) => sum + arg.rebuttals.length, 0)}
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </div>
          </div>
        </Box>
      )}

      {activeTab === 3 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>Debate Settings</Typography>
          <Card>
            <CardContent>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                <div>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={debateSettings.allowRebuttals}
                        onChange={(e) => setDebateSettings(prev => ({ ...prev, allowRebuttals: e.target.checked }))}
                      />
                    }
                    label="Allow Rebuttals"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={debateSettings.requireEvidence}
                        onChange={(e) => setDebateSettings(prev => ({ ...prev, requireEvidence: e.target.checked }))}
                      />
                    }
                    label="Require Evidence"
                  />
                </div>
                
                <div>
                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Max Arguments: {debateSettings.maxArguments}</Typography>
                    <Slider
                      value={debateSettings.maxArguments}
                      onChange={(e, value) => setDebateSettings(prev => ({ ...prev, maxArguments: value as number }))}
                      min={5}
                      max={20}
                      step={1}
                      marks
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Time Limit: {debateSettings.timeLimit}s</Typography>
                    <Slider
                      value={debateSettings.timeLimit}
                      onChange={(e, value) => setDebateSettings(prev => ({ ...prev, timeLimit: value as number }))}
                      min={60}
                      max={600}
                      step={30}
                      marks
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Min Confidence: {Math.round(debateSettings.minConfidence * 100)}%</Typography>
                    <Slider
                      value={debateSettings.minConfidence}
                      onChange={(e, value) => setDebateSettings(prev => ({ ...prev, minConfidence: value as number }))}
                      min={0.3}
                      max={1.0}
                      step={0.1}
                      marks
                    />
                  </Box>
                </div>
              </div>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Agent Detail Dialog */}
      <Dialog open={!!selectedAgent} onClose={() => setSelectedAgent(null)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: `${getAgentColor(selectedAgent?.bias || 'neutral')}.main` }}>
              {selectedAgent?.avatar}
            </Avatar>
            <Box>
              <Typography variant="h6">{selectedAgent?.name}</Typography>
              <Typography variant="body2" color="text.secondary">{selectedAgent?.role}</Typography>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedAgent && (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>{selectedAgent.personality}</Typography>
              
              <Typography variant="h6" sx={{ mb: 1 }}>Expertise Areas:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 3 }}>
                {selectedAgent.expertise.map((skill) => (
                  <Chip key={skill} label={skill} color="primary" variant="outlined" />
                ))}
              </Stack>
              
              <Typography variant="h6" sx={{ mb: 1 }}>Performance Metrics:</Typography>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
                <div>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
                    <Typography variant="h4" color="primary">{selectedAgent.totalArguments}</Typography>
                    <Typography variant="body2">Total Arguments</Typography>
                  </Box>
                </div>
                <div>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
                    <Typography variant="h4" color="success.main">{selectedAgent.winRate}%</Typography>
                    <Typography variant="body2">Win Rate</Typography>
                  </Box>
                </div>
                <div>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
                    <Typography variant="h4" color="warning.main">{selectedAgent.averageConfidence}%</Typography>
                    <Typography variant="body2">Avg Confidence</Typography>
                  </Box>
                </div>
              </div>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedAgent(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
