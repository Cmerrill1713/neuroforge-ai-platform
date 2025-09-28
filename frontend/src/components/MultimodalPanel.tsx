"use client"

import React, { useState } from 'react'
import Image from 'next/image'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Grid,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Image as ImageIcon,
  Close as CloseIcon,
  Visibility as VisibilityIcon,
  Help as HelpIcon,
  AutoAwesome as AIIcon,
  Search as SearchIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface UploadedImage {
  id: string
  file: File
  preview: string
  analysis?: string
}

interface MultimodalPanelProps {
  activeModel?: string
  onImageAnalysis?: (image: UploadedImage, analysis: string) => void
}

export function MultimodalPanel({ activeModel, onImageAnalysis }: MultimodalPanelProps) {
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showTutorial, setShowTutorial] = useState(false)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const newImage: UploadedImage = {
            id: Date.now().toString() + Math.random(),
            file,
            preview: e.target?.result as string
          }
          setUploadedImages(prev => [...prev, newImage])
        }
        reader.readAsDataURL(file)
      }
    })
  }

  const analyzeImage = async (image: UploadedImage) => {
    if (activeModel && activeModel !== 'llava:7b') {
      alert('Image analysis requires LLaVA model. Please switch to LLaVA 7B.')
      return
    }

    setIsAnalyzing(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const analysis = `This image shows a detailed analysis of the uploaded content. The AI has successfully processed the visual information and provided insights about the objects, colors, composition, and potential context within the image.`
      
      const updatedImage = { ...image, analysis }
      setUploadedImages(prev => prev.map(img => img.id === image.id ? updatedImage : img))
      
      if (onImageAnalysis) {
        onImageAnalysis(updatedImage, analysis)
      }
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const removeImage = (imageId: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== imageId))
  }

  const capabilities = [
    {
      name: 'LLaVA 7B',
      description: 'Image analysis, visual understanding',
      icon: <ImageIcon />,
      color: 'primary' as const
    },
    {
      name: 'Nomic Embed',
      description: 'Semantic search, knowledge retrieval',
      icon: <SearchIcon />,
      color: 'secondary' as const
    },
    {
      name: 'GPT-OSS 20B',
      description: 'Advanced reasoning, complex analysis',
      icon: <PsychologyIcon />,
      color: 'success' as const
    }
  ]

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, height: '100%', overflow: 'auto' }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Box>
          <Typography 
            variant="h4" 
            sx={{ 
              background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 700,
              mb: 1
            }}
          >
            👁️ Vision Assistant
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload images for AI analysis and visual understanding
          </Typography>
        </Box>
        <Tooltip title="How to use image analysis">
          <IconButton onClick={() => setShowTutorial(true)} color="primary">
            <HelpIcon />
          </IconButton>
        </Tooltip>
      </Stack>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: 'primary.main',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.dark',
                  backgroundColor: 'rgba(25, 118, 210, 0.04)'
                }
              }}
              onClick={() => document.getElementById('image-upload')?.click()}
            >
              <input
                id="image-upload"
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                style={{ display: 'none' }}
              />
              
              <Avatar sx={{ width: 64, height: 64, mx: 'auto', mb: 2, bgcolor: 'primary.light' }}>
                <UploadIcon sx={{ fontSize: 32 }} />
              </Avatar>
              
              <Typography variant="h6" gutterBottom>
                Click to upload images
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supports JPG, PNG, GIF, WebP
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Multimodal Capabilities */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
              <AIIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Multimodal Capabilities
              </Typography>
            </Stack>
            
            <Grid container spacing={2}>
              {capabilities.map((capability, index) => (
                <div key={index} style={{ width: '100%', padding: '8px' }}>
                  <Card 
                    variant="outlined"
                    sx={{ 
                      height: '100%',
                      border: `1px solid`,
                      borderColor: `${capability.color}.main`,
                      '&:hover': {
                        boxShadow: 2
                      }
                    }}
                  >
                    <CardContent>
                      <Stack alignItems="center" spacing={2} sx={{ textAlign: 'center' }}>
                        <Avatar sx={{ bgcolor: `${capability.color}.main` }}>
                          {capability.icon}
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                            {capability.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {capability.description}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Uploaded Images */}
      {uploadedImages.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Uploaded Images ({uploadedImages.length})
              </Typography>
              
              <Grid container spacing={2}>
                {uploadedImages.map((image) => (
                  <div key={image.id} style={{ width: '100%', padding: '8px' }}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ position: 'relative', mb: 2 }}>
                          <Image
                            src={image.preview}
                            alt="Uploaded"
                            width={400}
                            height={150}
                            style={{
                              width: '100%',
                              height: 150,
                              objectFit: 'cover',
                              borderRadius: 8
                            }}
                          />
                          <IconButton
                            size="small"
                            onClick={() => removeImage(image.id)}
                            sx={{
                              position: 'absolute',
                              top: 8,
                              right: 8,
                              bgcolor: 'rgba(0,0,0,0.5)',
                              color: 'white',
                              '&:hover': { bgcolor: 'rgba(0,0,0,0.7)' }
                            }}
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        </Box>
                        
                        <Stack spacing={1}>
                          <Typography variant="caption" color="text.secondary">
                            {image.file.name}
                          </Typography>
                          
                          {image.analysis ? (
                            <Alert severity="success" sx={{ fontSize: '0.75rem' }}>
                              Analysis complete
                            </Alert>
                          ) : (
                            <Button
                              size="small"
                              variant="contained"
                              startIcon={isAnalyzing ? <CircularProgress size={16} /> : <VisibilityIcon />}
                              onClick={() => analyzeImage(image)}
                              disabled={isAnalyzing}
                              fullWidth
                            >
                              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                            </Button>
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
      )}

      {/* Tutorial Dialog */}
      <Dialog open={showTutorial} onClose={() => setShowTutorial(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <HelpIcon color="primary" />
            <Typography variant="h6">How to Use Image Analysis</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <Typography>
              The Vision Assistant uses advanced AI models to analyze and understand images:
            </Typography>
            <Box component="ol" sx={{ pl: 2 }}>
              <li>Upload images by clicking the upload area</li>
              <li>Click &quot;Analyze&quot; on any uploaded image</li>
              <li>AI will process the image and provide insights</li>
              <li>View analysis results and recommendations</li>
            </Box>
            <Alert severity="info">
              For best results, use high-quality images with clear subjects and good lighting.
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTutorial(false)} variant="contained">
            Got it!
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}