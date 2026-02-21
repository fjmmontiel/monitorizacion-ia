import { ReactNode } from 'react';

import { reset } from './reset';
import { reboot } from './reboot';

const globalStyles = `${reset}\n${reboot}`;

export const AppThemeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <>
      <style>{globalStyles}</style>
      {children}
    </>
  );
};
