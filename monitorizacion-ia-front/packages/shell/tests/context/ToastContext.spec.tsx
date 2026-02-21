import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';

import { ToastProvider, useToast } from '../../src/context/ToastContext';

jest.mock('@internal-channels-components/toast', () => {
  const MockToast = React.forwardRef((_props, ref) => {
    React.useImperativeHandle(ref, () => ({
      show: jest.fn(),
    }));
    return <div data-testid="mock-toast" />;
  });
  MockToast.displayName = 'MockToast';

  return {
    Toast: MockToast,
    ToastTemplate: ({ message }: { message: string }) => <div>{message}</div>,
  };
});

describe('ToastContext', () => {
  const TestComponent = () => {
    const { showToast } = useToast();
    React.useEffect(() => {
      showToast({ severity: 'success', summary: 'Test', detail: 'Toast launched' });
    }, [showToast]);
    return <div>Test</div>;
  };
  TestComponent.displayName = 'TestComponent';

  it('should render ToastProvider and expose showToast', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>,
    );

    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByTestId('mock-toast')).toBeInTheDocument();
  });

  const BrokenComponent = () => {
    useToast(); // Esto lanza el error
    return null;
  };
  BrokenComponent.displayName = 'BrokenComponent';

  it('should throw error if useToast is used outside provider', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<BrokenComponent />)).toThrow('useToast must be used within a ToastProvider');
    consoleError.mockRestore();
  });
});
