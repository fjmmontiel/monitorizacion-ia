import { InputText } from '@internal-channels-components/input-text';

import { ContextItem, DataCliente, ItemType } from '../../domains/Context.domain';

import { ItemContainer } from './DataItem.styled';

export function DataClienteItem({ item }: { item: ContextItem<ItemType> }) {
  const cliente = item.data as DataCliente;
  return (
    <ItemContainer>
      <InputText disabled size="small" label="Nombre completo" value={cliente.nombreCompleto}></InputText>
      <InputText disabled size="small" label="NIF" value={cliente.nif}></InputText>
      <InputText disabled size="small" label="CLAPER" value={cliente.claper}></InputText>
      <InputText disabled size="small" label="Fecha de nacimiento" value={cliente.fechaNacimiento}></InputText>
      <InputText disabled size="small" label="Dirección" value={cliente.direccion}></InputText>
      <InputText disabled size="small" label="Email" value={cliente.email}></InputText>
      <InputText disabled size="small" label="Teléfono" value={cliente.telefono}></InputText>
    </ItemContainer>
  );
}
