import { InputText } from '@internal-channels-components/input-text';

import { ContextItem, DataGestor, ItemType } from '../../domains/Context.domain';

import { ItemContainer } from './DataItem.styled';

export function DataGestorItem({ item }: { item: ContextItem<ItemType> }) {
  const cliente = item.data as DataGestor;
  return (
    <ItemContainer>
      <InputText disabled size="small" label="Código" value={cliente.codigo}></InputText>
      <InputText disabled size="small" label="Centro" value={cliente.centro}></InputText>
    </ItemContainer>
  );
}
