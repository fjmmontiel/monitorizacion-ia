import { InputText } from '@internal-channels-components/input-text';
import { Accordion, AccordionTab } from '@internal-channels-components/accordion';
import { Tooltip } from '@internal-channels-components/tooltip';

import { ContextItem, DataProducto, RecomendacionHipoteca, ItemType } from '../../domains/Context.domain';

import { ItemContainer, SubseccionContainer } from './DataItem.styled';

export function DataRecomendacionItem({ item }: { item: ContextItem<ItemType> }) {
  const recomendacion = item.data as RecomendacionHipoteca;
  const ingresos = recomendacion.ingresos
    ? recomendacion.ingresos.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })
    : '';

  // Helpers
  const s = (v?: string | null) => v ?? '';
  const labelize = (key: string) =>
    key
      .replace(/_/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace(/\b\w/g, c => c.toUpperCase());

  return (
    <ItemContainer>
      <InputText disabled size="small" label="Tipo de interés" value={(recomendacion.tipoInteres ?? []).join(', ')} />
      <InputText disabled size="small" label="Ingresos" value={ingresos} />
      <InputText disabled size="small" label="Edad" value={String(recomendacion.edad ?? '')} />
      <InputText
        disabled
        size="small"
        label="Certificación energética"
        value={s(recomendacion.certificacionEnergeticaVivienda)}
      />
      {/* <InputText disabled size="small" label="Fecha recomendación" value={s(recomendacion.timestamp)} /> */}

      <SubseccionContainer>
        <Accordion>
          {recomendacion.resultadoRecomendacion.map((producto: DataProducto) => (
            <AccordionTab
              key={producto.codigoProducto.administrativo}
              header={`${producto.codigoProducto.administrativo} - ${producto.nombreProducto}`}>
              {/* ===== Datos básicos del producto ===== */}
              <ItemContainer>
                <InputText disabled size="small" label="Nombre del producto" value={s(producto.nombreProducto)} />
                <InputText
                  disabled
                  size="small"
                  label="Código comercial"
                  value={s(producto.codigoProducto?.comercial)}
                />
                <InputText
                  disabled
                  size="small"
                  label="Código administrativo"
                  value={s(producto.codigoProducto?.administrativo)}
                />
                <InputText disabled size="small" label="Público objetivo" value={s(producto.publicoObjetivo)} />
                <InputText disabled size="small" label="Descripción" value={s(producto.descripcionProducto)} />
              </ItemContainer>

              {/* ===== Tarifas (sin condicionesFinancieras ni bloques de bonificación) ===== */}
              <ItemContainer>
                <InputText
                  disabled
                  size="small"
                  label="Tipo interés fijo con bonificación por vinculación"
                  value={s(producto.tarifas?.tipoDeInteresFijoConBonificacionPorVinculacion)}
                />

                {/* Tipos de interés (map del Record<string, string>) */}
                {Object.entries(producto.tarifas?.tiposInteres ?? {}).map(([clave, valor]) => (
                  <InputText
                    key={`tipoInteres-${clave}`}
                    disabled
                    size="small"
                    label={`Tipo de interés - ${labelize(clave)}`}
                    value={s(valor)}
                  />
                ))}

                {/* Comisiones (map del Record<string, string>) */}
                {Object.entries(producto.tarifas?.comisiones ?? {}).map(([clave, valor]) => (
                  <InputText
                    key={`comision-${clave}`}
                    disabled
                    size="small"
                    label={`Comisión - ${labelize(clave)}`}
                    value={s(valor)}
                  />
                ))}

                <InputText disabled size="small" label="Bonificación máxima" value={s(producto.bonificacionMaxima)} />
                <InputText
                  disabled
                  size="small"
                  label="Periodicidad de revisión"
                  value={s(producto.periodicidadDeRevision)}
                />
              </ItemContainer>

              {/* ===== Atribuciones y consideraciones ===== */}
              <ItemContainer>
                <InputText
                  disabled
                  size="small"
                  label="Atribuciones en condiciones financieras"
                  value={s(producto.atribucionesEnCondicionesFinancieras)}
                />
                <InputText
                  disabled
                  size="small"
                  label="Atribuciones en concesión de operaciones"
                  value={s(producto.atribucionesEnConcesionDeOperaciones)}
                />
                <InputText
                  disabled
                  size="small"
                  label="Consideraciones generales"
                  value={s(producto.consideracionesGenerales)}
                />
                <Tooltip content={s(producto.argumentarioComercial)} target=".argumento-comercial"></Tooltip>
                <InputText
                  disabled
                  size="small"
                  label="Argumentario comercial"
                  className="argumento-comercial"
                  value={s(producto.argumentarioComercial)}
                />
              </ItemContainer>
            </AccordionTab>
          ))}
        </Accordion>
      </SubseccionContainer>
    </ItemContainer>
  );
}
