import React from 'react';
import { Outlet } from 'react-router-dom';

import { MainContent } from './TopNavLayout.styles';

export interface TopNavLayoutProps {
  userInfo?: {
    firstName?: string;
    lastName?: string;
    nif?: string;
  };
}

export const TopNavLayout: React.FC<TopNavLayoutProps> = () => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f9fafb' }}>
      {' '}
      <MainContent>
        <Outlet />
      </MainContent>
    </div>
  );
};
