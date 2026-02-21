import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { global } from '@internal-channels-components/theme';

import { DataClienteItem } from '#/shell/components/DataItems/DataClienteItem';
import { DataGestorItem } from '#/shell/components/DataItems/DataGestorItem';
import { DataIntervinienteItem } from '#/shell/components/DataItems/DataIntervinienteItem';
import { DataOperacionItem } from '#/shell/components/DataItems/DataOperacionItem';
import { DataPreevalItem } from '#/shell/components/DataItems/DataPreevalItem';
import { DataRecomendacionItem } from '#/shell/components/DataItems/DataRecomendacionItem';
import { AppThemeProvider } from '#/shell/theme';
import { DataMuestraInteresItem } from '#/shell/components/DataItems/DataMuestraInteresItem';

import { ContextItem, DataCliente, DataGestor } from '../../../src/domains/Context.domain';

// Mock de Accordion y AccordionTab
jest.mock('@internal-channels-components/input-text', () => ({
  InputText: ({ value }: { value: string }) => <div>{value}</div>,
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

function renderWithTheme(ui: React.ReactElement) {
  return render(<AppThemeProvider theme={global}>{ui}</AppThemeProvider>);
}

describe('DataClienteItem', () => {
  it('renderiza correctamente los datos del cliente', () => {
    const clienteData = new DataCliente({
      nif: '12345678A',
      claper: 'CLP001',
      fechaNacimiento: '1980-01-01',
      nombreCompleto: 'Juan Pérez',
      email: 'juan@example.com',
      telefono: '600123456',
      direccion: 'Calle Falsa 123',
    });

    const item = new ContextItem({
      id: 'cliente-1',
      name: 'Juan Pérez',
      item_type: 'DataCliente',
      tab: '',
      llm_header: '',
      data: clienteData,
    });

    renderWithTheme(<DataClienteItem item={item} />);

    expect(screen.getByText(/Juan Pérez/)).toBeInTheDocument();
    expect(screen.getByText(/12345678A/)).toBeInTheDocument();
    expect(screen.getByText(/CLP001/)).toBeInTheDocument();
    expect(screen.getByText(/1980-01-01/)).toBeInTheDocument();
    expect(screen.getByText(/juan@example.com/)).toBeInTheDocument();
    expect(screen.getByText(/600123456/)).toBeInTheDocument();
    expect(screen.getByText(/Calle Falsa 123/)).toBeInTheDocument();
  });
});

describe('DataGestorItem', () => {
  it('renderiza correctamente los datos del gestor', () => {
    const gestorData = new DataGestor({
      codigo: 'GEST001',
      centro: 'Centro Madrid',
    });

    const item = new ContextItem({
      id: 'gestor-1',
      name: 'Gestor Principal',
      item_type: 'DataGestor',
      tab: '',
      llm_header: '',
      data: gestorData,
    });

    renderWithTheme(<DataGestorItem item={item} />);

    expect(screen.getByText(/GEST001/)).toBeInTheDocument();
    expect(screen.getByText(/Centro Madrid/)).toBeInTheDocument();
  });
});

describe('DataIntervinienteItem', () => {
  it('renderiza correctamente los datos del interviniente', () => {
    const item = new ContextItem({
      id: 'inter-1',
      name: 'Interviniente Uno',
      item_type: 'DataInterviniente',
      tab: '',
      llm_header: '',
      data: {
        datos_contacto: {
          email: 'inter@example.com',
          prefijo: '+34',
          movil: '600123456',
          paisTelefono: '011', // opcional, la clase pone '' si no viene
          direccion: {
            tipoVia: 'Calle',
            domicilio: 'Falsa',
            numero: '123',
            portal: 'A',
            bloque: 'B',
            escalera: '1',
            puerta: '2',
            planta: '3',
            parcela: '4',
            km: '5',
            poblacion: 'Madrid',
            codPostal: '28080',
            codProvincia: '28',
            // codPais y restoDireccion son opcionales
          },
        },
        infConsumidor: 'S',
        paisResidencia: '11',

        // Ajustado a claves esperadas por la clase
        datos_personales_y_profesionales: {
          profesion: 'Ingeniero',
        },
        datos_vivienda_habitual: {
          sitViviendaHab: 'Propiedad',
        },
        datos_ingresos: {
          ingresoFijos: 3000,
        },
        datos_situacion_economica: {
          cuotasOOEE: 10000,
        },
      },
    });

    renderWithTheme(<DataIntervinienteItem item={item} />);

    expect(screen.getByText(/1. Datos personales y profesionales/)).toBeInTheDocument();
    expect(screen.getByText(/2. Datos de contacto/)).toBeInTheDocument();
    expect(screen.getByText(/3. Vivienda habitual/)).toBeInTheDocument();
    expect(screen.getByText(/4. Ingresos/)).toBeInTheDocument();
    expect(screen.getByText(/5. Situación económica/)).toBeInTheDocument();
    expect(screen.getByText(/6. Datos generales/)).toBeInTheDocument(); // profesion
  });
});

describe('DataOperacionItem', () => {
  it('renderiza correctamente los datos de la operación', () => {
    const item = new ContextItem({
      id: 'op-1',
      name: 'Operación Uno',
      item_type: 'DataOperacion',
      tab: '',
      llm_header: '',
      data: {
        subproducto: 'Hipoteca Fija',
        plazoTotalU: 'años',
        plazoTotal: 30,
        indUsoResidencial: 'S',
        indTipoIntSS: 'F',
        importeSolicitado: 250000,
        finalidad: '2112',
      },
    });

    renderWithTheme(<DataOperacionItem item={item} />);

    expect(screen.getByText(/Hipoteca Fija/)).toBeInTheDocument();
    expect(screen.getByText(/30 años/)).toBeInTheDocument();
    expect(screen.getByText(/Sí/)).toBeInTheDocument();
    expect(screen.getByText(/Fijo/)).toBeInTheDocument();
    expect(screen.getByText(/250.000,00 €/)).toBeInTheDocument(); // Formato español
    expect(screen.getByText(/Adquisición 1ª residencia/)).toBeInTheDocument();
  });
});

describe('DataPreevalItem', () => {
  it('renderiza correctamente los datos de preevaluación', () => {
    const item = new ContextItem({
      id: 'preeval-1',
      name: 'Preevaluación Uno',
      item_type: 'DataPreeval',
      tab: '',
      llm_header: '',
      data: {
        valorTasa: 120000,
        precioVivienda: 200000,
        importeTotalInversion: 50000,
        tipoInmu: 'PSO',
        provincia: '28',
        hipVvdaHab: 'S',
        codEstadoInmu: 'N',
      },
    });

    renderWithTheme(<DataPreevalItem item={item} />);

    expect(screen.getByText(/120.000,00 €/)).toBeInTheDocument();
    expect(screen.getByText(/200.000,00 €/)).toBeInTheDocument();
    expect(screen.getByText(/50.000,00 €/)).toBeInTheDocument();
    expect(screen.getByText(/Piso/)).toBeInTheDocument();
    expect(screen.getByText(/Madrid/)).toBeInTheDocument();
    expect(screen.getByText(/Sí/)).toBeInTheDocument();
    expect(screen.getByText(/TERMINADO NUEVO/)).toBeInTheDocument();
  });
});

describe('DataRecomendacionItem', () => {
  it('renderiza correctamente todos los datos de recomendación y productos', () => {
    const item = new ContextItem({
      id: 'rec-1',
      name: 'Recomendación Uno',
      item_type: 'RecomendacionHipoteca',
      tab: '',
      llm_header: '',
      data: {
        tipo_interes: ['Fijo', 'Variable'],
        ingresos: 45000,
        edad: 35,
        certificacion_energetica_vivienda: 'CERTIFICACION A',
        timestamp: '2025-10-21',
        resultado_recomendacion: [
          {
            nombre_producto: 'Hipoteca Fija 30 años',
            codigo_producto: {
              comercial: 'COM30',
              administrativo: 'HF30',
            },
            publico_objetivo: 'Jóvenes',
            descripcion_producto: 'Hipoteca a tipo fijo',
            tarifas: {
              tipoDeInteresFijoConBonificacionPorVinculacion: '2.5%',
              tiposInteres: {
                inicial: '2.8%',
                resto: '3.0%',
              },
              comisiones: {
                apertura: '0%',
                cancelacion: '1%',
              },
            },
            bonificacion_maxima: '2%',
            periodicidad_de_revision: 'Anual',
            atribuciones_en_condiciones_financieras: 'Aprobación automática',
            atribuciones_en_concesion_de_operaciones: 'Manual',
            consideraciones_generales: 'Producto recomendado',
            argumentario_comercial: 'Ideal para perfiles estables',
          },
        ],
      },
    });

    renderWithTheme(<DataRecomendacionItem item={item} />);

    // Datos generales
    expect(screen.getByText(/Fijo, Variable/)).toBeInTheDocument();
    expect(screen.getByText(/45.000,00 €/)).toBeInTheDocument();
    expect(screen.getByText(/35/)).toBeInTheDocument();
    expect(screen.getByText(/CERTIFICACION A/)).toBeInTheDocument();
    // expect(screen.getByText(/2025-10-21/)).toBeInTheDocument();

    // Datos del producto
    expect(screen.getByText(/HF30 - Hipoteca Fija 30 años/)).toBeInTheDocument();
    expect(screen.getByText(/Hipoteca a tipo fijo/)).toBeInTheDocument();
    expect(screen.getByText(/Jóvenes/)).toBeInTheDocument();
    expect(screen.getByText(/COM30/)).toBeInTheDocument();

    // Tarifas
    expect(screen.getByText(/2.5%/)).toBeInTheDocument();

    // Bonificación y revisión
    expect(screen.getByText(/1%/)).toBeInTheDocument();
    expect(screen.getByText(/Anual/)).toBeInTheDocument();

    // Atribuciones y consideraciones
    expect(screen.getByText(/Aprobación automática/)).toBeInTheDocument();
    expect(screen.getByText(/Manual/)).toBeInTheDocument();
    expect(screen.getByText(/Producto recomendado/)).toBeInTheDocument();
    expect(screen.getByText(/Ideal para perfiles estables/)).toBeInTheDocument();
  });
});

describe('DataMuestraItenresItem', () => {
  it('renderiza correctamente los datos de muestra', () => {
    const item = new ContextItem({
      id: 'muestra-1',
      name: 'Muestra de Interés Uno',
      item_type: 'DataMuestraInteres',
      tab: '',
      llm_header: '',
      data: {
        resultados_log_operacional: '',
        resultado_muestra_interes: {
          documento: 'https://www.google.com',
          numExpeSG: {
            anyo: '2025',
            centro: '7383',
            idExpe: '00000323',
          },
        },
      },
    });

    renderWithTheme(<DataMuestraInteresItem item={item} />);

    expect(screen.getByText(/2025/)).toBeInTheDocument();
    expect(screen.getByText(/7383/)).toBeInTheDocument();
    expect(screen.getByText(/00000323/)).toBeInTheDocument();
  });
});
