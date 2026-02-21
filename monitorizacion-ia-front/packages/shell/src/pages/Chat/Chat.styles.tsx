/* istanbul ignore file */
import styled from 'styled-components';

export const Main = styled.main<{ $isSesionDetail: boolean }>`
  flex-grow: 1;
  padding: 0;
  display: flex;
  height: 100vh;
  max-height: ${({ $isSesionDetail }) => ($isSesionDetail ? 'calc(100vh - 88px)' : '100vh')};
`;

export const LeftPanel = styled.div`
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
`;

export const Divider = styled.div`
  width: 4px;
  background: #d1d5db;
  cursor: col-resize;
`;

export const RightPanel = styled.div`
  background: #f3f4f6;
`;
