import React from 'react';
import {
  Box,
  Snackbar,
  Alert,
  Slide,
  SlideProps,
} from '@mui/material';
import { useAppContext } from '../../contexts/AppContext';

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

export const NotificationSystem: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const { notifications } = state;

  const handleClose = (notificationId: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: notificationId });
  };

  return (
    <Box>
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={5000}
          onClose={() => handleClose(notification.id)}
          TransitionComponent={SlideTransition}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          sx={{ mb: 1 }}
        >
          <Alert
            onClose={() => handleClose(notification.id)}
            severity={notification.type}
            variant="filled"
            sx={{
              backgroundColor: getAlertColor(notification.type),
              color: 'white',
              '& .MuiAlert-icon': {
                color: 'white',
              },
            }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

function getAlertColor(type: string): string {
  switch (type) {
    case 'success': return '#4caf50';
    case 'error': return '#f44336';
    case 'warning': return '#ff9800';
    case 'info': return '#2196f3';
    default: return '#9e9e9e';
  }
}
