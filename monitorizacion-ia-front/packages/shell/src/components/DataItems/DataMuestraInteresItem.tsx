import { InputText } from '@internal-channels-components/input-text';
import { Button } from '@internal-channels-components/button';

import { ContextItem, ItemType, ResultadoMuestraInteres } from '../../domains/Context.domain';

import { ItemContainer } from './DataItem.styled';

export function DataMuestraInteresItem({ item }: { item: ContextItem<ItemType> }) {
  const muestra = item.data.resultadoMuestraInteres as ResultadoMuestraInteres;
  return (
    <ItemContainer>
      <InputText disabled size="small" label="Año" value={muestra.numExpeSG?.anyo}></InputText>
      <InputText disabled size="small" label="Centro" value={muestra.numExpeSG?.centro}></InputText>
      <InputText disabled size="small" label="Expediente" value={muestra.numExpeSG?.idExpe}></InputText>
      <Button label="Ver documento" onClick={() => window.open(muestra.documento, '_blank')}></Button>
    </ItemContainer>
  );
}
