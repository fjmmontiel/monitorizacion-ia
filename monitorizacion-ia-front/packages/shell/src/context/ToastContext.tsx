import { Toast, ToastRef, ToastTemplate } from '@internal-channels-components/toast';
import React, { createContext, useContext, useRef, ReactNode } from 'react';

interface ToastProps {
  severity: 'info' | 'success' | 'warn' | 'error' | 'secondary';
  summary: string;
  detail: string;
  sticky?: boolean;
  life?: number;
  position?: 'top-left' | 'top-right' | 'top-center' | 'bottom-left' | 'bottom-right' | 'bottom-center';
}

interface ToastContextType {
  showToast: (props: ToastProps) => void;
}

export const useToast = () => {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

const ToastContext = createContext<ToastContextType | undefined>(undefined);

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const toastRef = useRef<ToastRef>(null);

  const showToast = (value: ToastProps) => {
    toastRef.current?.show({
      ...value,
      content: ({ message }) => <ToastTemplate message={message} />,
    });
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <Toast ref={toastRef} />
    </ToastContext.Provider>
  );
};
