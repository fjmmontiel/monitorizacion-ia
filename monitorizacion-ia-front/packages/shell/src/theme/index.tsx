import { DefaultTheme, ThemeProvider, createGlobalStyle } from '@internal-channels-components/theme';
import { ReactNode } from 'react';

import { reset } from './reset';
import { reboot } from './reboot';

const GlobalStyles = createGlobalStyle`
  ${reset};
  ${reboot};
`;

export const AppThemeProvider = ({ children, theme }: { children: ReactNode; theme: DefaultTheme }) => {
  return (
    <>
      <GlobalStyles />
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </>
  );
};
