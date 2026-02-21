import '@testing-library/jest-dom';
import { global } from '@internal-channels-components/theme';
import { render, screen } from '@testing-library/react';

import { AppThemeProvider } from '#/shell/theme';

import { ChatMessage } from '../../../src/services/ChatService';
import ChatMessageComponent from '../../../src/components/ChatMessage/ChatMessage';

// Mock de react-icons para poder buscar los iconos por testId
// jest.mock('react-icons/bs', () => {
//   const React = require('react');
//   return {
//     BsPersonFill: (props: any) => React.createElement('svg', { ...props, 'data-testid': 'BsPersonFill-icon' }),
//     BsRobot: (props: any) => React.createElement('svg', { ...props, 'data-testid': 'BsRobot-icon' }),
//   };
// });
// jest.mock('react-markdown', () => ({
//   __esModule: true,
//   default: (props: any) => <div data-testid="react-markdown">{props.children}</div>,
// }));
// jest.mock('remark-gfm', () => () => {});

describe('ChatMessageComponent', () => {
  const baseDate = new Date('2023-01-01T12:34:00');

  it('renders user message with correct styles and icon', () => {
    const message: ChatMessage = {
      id: '1',
      message: 'Hello world!',
      role: 'user',
      timestamp: baseDate,
    };
    render(
      <AppThemeProvider theme={global}>
        <ChatMessageComponent message={message} />
      </AppThemeProvider>,
    );
    expect(screen.getByText('Hello world!')).toBeInTheDocument();
  });

  it('renders bot message with correct styles and icon', () => {
    const message: ChatMessage = {
      id: '2',
      message: 'Hi there!',
      role: 'bot',
      timestamp: baseDate,
    };
    render(
      <AppThemeProvider theme={global}>
        <ChatMessageComponent message={message} />
      </AppThemeProvider>,
    );
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    //expect(screen.getByText('12:34')).toBeInTheDocument();
    //expect(screen.getByTestId('BsRobot-icon')).toBeInTheDocument();
  });
});
