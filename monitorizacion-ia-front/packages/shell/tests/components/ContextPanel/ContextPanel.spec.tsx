import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { global } from '@internal-channels-components/theme';

import { AppThemeProvider } from '#/shell/theme';

import { useContextManager } from '../../../src/hooks/useContextManager';
import { ContextItem } from '../../../src/domains/Context.domain';
import { ContextPanel } from '../../../src/components/ContextPanel/ContextPanel';

jest.mock('../../../src/hooks/useContextManager');

// Mock de los componentes de tipo de datos
jest.mock('../../../src/components/DataItems/DataClienteItem', () => ({
  DataClienteItem: ({ item }: { item: ContextItem }) => <div data-testid="cliente">{item.name}</div>,
}));
jest.mock('../../../src/components/DataItems/DataGestorItem', () => ({
  DataGestorItem: ({ item }: { item: ContextItem }) => <div data-testid="gestor">{item.name}</div>,
}));
jest.mock('../../../src/components/DataItems/DataOperacionItem', () => ({
  DataOperacionItem: ({ item }: { item: ContextItem }) => <div data-testid="operacion">{item.name}</div>,
}));
jest.mock('../../../src/components/DataItems/DataIntervinienteItem', () => ({
  DataIntervinienteItem: ({ item }: { item: ContextItem }) => <div data-testid="interviniente">{item.name}</div>,
}));
jest.mock('../../../src/components/DataItems/DataPreevalItem', () => ({
  DataPreevalItem: ({ item }: { item: ContextItem }) => <div data-testid="preeval">{item.name}</div>,
}));
jest.mock('../../../src/components/DataItems/DataRecomendacionItem', () => ({
  DataRecomendacionItem: ({ item }: { item: ContextItem }) => <div data-testid="recomendacion">{item.name}</div>,
}));

// Mock de Accordion y AccordionTab
jest.mock('@internal-channels-components/accordion', () => ({
  Accordion: ({ children }: { children: React.ReactNode }) => <div data-testid="accordion">{children}</div>,
  AccordionTab: ({ children, header }: { children: React.ReactNode; header: string }) => (
    <div data-testid="accordion-tab">
      <div>{header}</div>
      {children}
    </div>
  ),
}));

describe('ContextPanel', () => {
  beforeEach(() => {
    (useContextManager as jest.Mock).mockReturnValue({
      items: [
        new ContextItem({ id: '1', name: 'Cliente Uno', item_type: 'DataCliente', tab: '', llm_header: '', data: {} }),
        new ContextItem({ id: '2', name: 'Gestor Dos', item_type: 'DataGestor', tab: '', llm_header: '', data: {} }),
        new ContextItem({
          id: '3',
          name: 'Operación Tres',
          item_type: 'DataOperacion',
          tab: '',
          llm_header: '',
          data: {},
        }),
        new ContextItem({
          id: '4',
          name: 'Interviniente Cuatro',
          item_type: 'DataInterviniente',
          tab: '',
          llm_header: '',
          data: {},
        }),
        new ContextItem({
          id: '5',
          name: 'Preeval Cinco',
          item_type: 'DataPreeval',
          tab: '',
          llm_header: '',
          data: {},
        }),
        new ContextItem({
          id: '6',
          name: 'Recomendación Seis',
          item_type: 'RecomendacionHipoteca',
          tab: '',
          llm_header: '',
          data: {},
        }),
        new ContextItem({
          id: '7',
          name: 'Desconocido Siete',
          item_type: 'TipoInexistente',
          tab: '',
          llm_header: '',
          data: {},
        }),
        new ContextItem({ id: '8', name: 'Sin tipo', item_type: null, tab: '', llm_header: '', data: {} }),
      ],
    });
  });

  it('renderiza todos los tipos conocidos correctamente', () => {
    render(
      <AppThemeProvider theme={global}>
        <ContextPanel />
      </AppThemeProvider>,
    );

    expect(screen.getByTestId('cliente')).toHaveTextContent('Cliente Uno');
    expect(screen.getByTestId('gestor')).toHaveTextContent('Gestor Dos');
    expect(screen.getByTestId('operacion')).toHaveTextContent('Operación Tres');
    expect(screen.getByTestId('interviniente')).toHaveTextContent('Interviniente Cuatro');
    expect(screen.getByTestId('preeval')).toHaveTextContent('Preeval Cinco');
    expect(screen.getByTestId('recomendacion')).toHaveTextContent('Recomendación Seis');
  });

  it('renderiza tipos desconocidos con mensaje de fallback', () => {
    render(
      <AppThemeProvider theme={global}>
        <ContextPanel />
      </AppThemeProvider>,
    );
    expect(screen.getByText('Tipo desconocido: Desconocido Siete')).toBeInTheDocument();
    expect(screen.getByText('Tipo desconocido: Sin tipo')).toBeInTheDocument();
  });

  it('renderiza todos los AccordionTab correctamente', () => {
    render(
      <AppThemeProvider theme={global}>
        <ContextPanel />
      </AppThemeProvider>,
    );
    const tabs = screen.getAllByTestId('accordion-tab');
    expect(tabs.length).toBeGreaterThanOrEqual(6); // los tipos conocidos
  });
});
