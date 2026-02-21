/* istanbul ignore file */
import styled from 'styled-components';
import { DataTableComponent } from '@internal-channels-components/data-table';

export const Main = styled.main`
  flex-grow: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
`;

export const Titulo = styled.p`
  color: ${({ theme }) => theme.colors.content.static.primary};
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'l',
      weight: 'bold',
    })};
`;

export const StyledDataTable = styled(DataTableComponent)``;

export const ActionButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  /* visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  pointer-events: none;
  cursor: unset;

  .p-datatable-tbody > tr:hover & {
    visibility: visible;
    opacity: 1;
    cursor: pointer;
    pointer-events: initial;
  } */
`;
