import { InputText } from '@internal-channels-components/input-text';

import { ContextItem, DataPreeval, ItemType } from '../../domains/Context.domain';
import {
  traducciontipoInmueble,
  traduccionProvincia,
  traduccionSiNo,
  traduccionEstadoInmueble,
} from '../../domains/Traducciones.domain';

import { ItemContainer } from './DataItem.styled';

export function DataPreevalItem({ item }: { item: ContextItem<ItemType> }) {
  const preeval = item.data as DataPreeval;

  const formatEuro = (value: number) =>
    value ? value.toLocaleString('es-ES', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 }) : '';

  return (
    <ItemContainer>
      <InputText disabled size="small" label="Valor de tasa" value={formatEuro(preeval.valorTasa)} />
      <InputText disabled size="small" label="Precio vivienda" value={formatEuro(preeval.precioVivienda)} />
      <InputText
        disabled
        size="small"
        label="Importe total de inversión"
        value={formatEuro(preeval.importeTotalInversion)}
      />
      <InputText disabled size="small" label="Tipo inmueble" value={traducciontipoInmueble[preeval.tipoInmu]} />
      <InputText disabled size="small" label="Provincia" value={traduccionProvincia[preeval.provincia]} />
      <InputText disabled size="small" label="Hipoteca vivienda habitual" value={traduccionSiNo[preeval.hipVvdaHab]} />
      <InputText
        disabled
        size="small"
        label="Estado inmueble"
        value={traduccionEstadoInmueble[preeval.codEstadoInmu]}
      />
    </ItemContainer>
  );
}
