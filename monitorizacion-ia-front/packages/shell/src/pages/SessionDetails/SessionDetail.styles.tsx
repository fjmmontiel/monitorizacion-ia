/* istanbul ignore file */
import styled from 'styled-components';

export const Main = styled.div`
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

export const Header = styled.div`
  padding: 16px;
  display: flex;
  flex-direction: row;

  p {
    margin-left: 32px;
    ${({ theme }) =>
      theme.typography.generateFontStyle({
        size: 'm',
        weight: 'regular',
      })};
  }
`;
