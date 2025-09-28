import { useState, useEffect } from 'react';
import { useTheme, useMediaQuery } from '@mui/material';
import { AppState } from '../types';

interface UseAppStateReturn extends AppState {
  handleDrawerToggle: () => void;
  handlePanelChange: (panelId: string) => void;
}

export const useAppState = (): UseAppStateReturn => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activePanel, setActivePanel] = useState('chat');
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handlePanelChange = (panelId: string) => {
    setActivePanel(panelId);
  };

  return {
    activePanel,
    sidebarOpen,
    isMobile,
    handleDrawerToggle,
    handlePanelChange
  };
};
