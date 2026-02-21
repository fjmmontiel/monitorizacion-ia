import { InputText } from '@internal-channels-components/input-text';

import { ContextItem, DataOperacion, ItemType } from '../../domains/Context.domain';
import { traduccionTipoInteres, traduccionFinalidad, traduccionSiNo } from '../../domains/Traducciones.domain';

import { ItemContainer } from './DataItem.styled';

export function DataOperacionItem({ item }: { item: ContextItem<ItemType> }) {
  const operacion = item.data as DataOperacion;

  const plazo = operacion.plazoTotal ? `${operacion.plazoTotal} ${operacion.plazoTotalU}` : '';
  const importeFormateado = operacion.importeSolicitado
    ? operacion.importeSolicitado.toLocaleString('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
      })
    : '';

  return (
    <ItemContainer>
      <InputText disabled size="small" label="Subproducto" value={operacion.subproducto} />
      <InputText disabled size="small" label="Plazo total" value={plazo} />
      <InputText disabled size="small" label="Uso residencial" value={traduccionSiNo[operacion.indUsoResidencial]} />
      <InputText disabled size="small" label="Tipo interés SS" value={traduccionTipoInteres[operacion.indTipoIntSS]} />
      <InputText disabled size="small" label="Importe solicitado" value={importeFormateado} />
      <InputText disabled size="small" label="Finalidad" value={traduccionFinalidad[operacion.finalidad]} />
    </ItemContainer>
  );
}
