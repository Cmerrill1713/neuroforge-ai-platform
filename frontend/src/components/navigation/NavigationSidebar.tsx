import React from 'react';
import {
  Box,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { Panel } from '../../types';

interface NavigationSidebarProps {
  panels: Panel[];
  activePanel: string;
  onPanelChange: (panelId: string) => void;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  panels,
  activePanel,
  onPanelChange,
}) => {
  const sidebarContent = (
    <Box sx={{
      width: 320,
      height: '100%',
      background: 'linear-gradient(135deg, rgba(10, 10, 10, 0.95) 0%, rgba(20, 20, 20, 0.95) 100%)',
      backdropFilter: 'blur(20px)',
      borderRight: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <Toolbar sx={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <Typography variant="h6" noWrap component="div" sx={{ color: 'white', fontWeight: 600 }}>
          Navigation
        </Typography>
      </Toolbar>
      <List sx={{ p: 1 }}>
        {panels.map((panel) => (
          <ListItem key={panel.id} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={activePanel === panel.id}
              onClick={() => onPanelChange(panel.id)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: `${panel.color}20`,
                  transform: 'translateX(4px)',
                },
                '&.Mui-selected': {
                  backgroundColor: `${panel.color}30`,
                  borderLeft: `4px solid ${panel.color}`,
                  '&:hover': {
                    backgroundColor: `${panel.color}40`,
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: activePanel === panel.id ? panel.color : 'rgba(255, 255, 255, 0.7)' }}>
                {panel.icon}
              </ListItemIcon>
              <ListItemText
                primary={panel.name}
                sx={{
                  color: activePanel === panel.id ? 'white' : 'rgba(255, 255, 255, 0.8)',
                  fontWeight: activePanel === panel.id ? 600 : 400
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return sidebarContent;
};
