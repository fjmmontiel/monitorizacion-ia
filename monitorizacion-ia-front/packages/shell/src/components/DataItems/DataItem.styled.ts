import styled from 'styled-components';

export const ItemContainer = styled.div`
  display: flex;
  gap: 36px;
  flex-direction: column;
  flex-wrap: nowrap;
  padding: 16px;
`;

export const SubseccionContainer = styled.div`
  && .p-accordion .p-accordion-header .p-accordion-header-link .p-accordion-header-text {
    ${({ theme }) =>
      theme.typography.generateFontStyle({
        size: 'xs',
      })};
  }
`;
