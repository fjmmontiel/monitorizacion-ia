/* istanbul ignore file */
import styled from 'styled-components';

export const ContextPanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  max-height: 100vh;
  height: 100%;
  overflow-y: auto;

  .p-accordion-header-text {
    ${({ theme }) =>
      theme.typography.generateFontStyle({
        size: 'm',
        weight: 'bold',
      })};
  }
`;

export const ItemContainer = styled.div`
  border: 1px solid #ccc;
  padding: 8px;
  margin: 4px;
  border-radius: 4px;
  background: #fafbfc;
`;

/* Contenedor del estado vacío con columna centrada y separación */
export const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding: 16px;
  justify-content: center;
  flex-grow: 1;
`;

export const EmptyTitle = styled.h3`
  margin: 0;
  color: ${({ theme }) => theme.colors.content.interactive.primary.disabled};
  margin-top: -36px;
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'l',
      weight: 'bold',
    })};
`;

export const EmptySubtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.content.static.disabled};
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'm',
      weight: 'bold',
    })};
`;

export const Title = styled.div`
  display: flex;
  align-items: center;
  color: ${({ theme }) => theme.colors.content.static.secondary};
  border-bottom: 2px solid ${({ theme }) => theme.colors.border.static.primary};
  padding: 16px 8px;
  margin: 0;
  line-height: 12px !important;
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'm',
      weight: 'bold',
    })};
  span {
    padding-left: 8px;
    vertical-align: text-top;
  }

  .p-button {
    flex: 0 0 auto;
    align-self: flex-end;
    margin-left: auto;
  }
`;

export const FooterContainer = styled.div`
  padding: 16px;
`;

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

export const Label = styled.label`
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: block;
`;
