import { css, styled } from '@internal-channels-components/theme';

export const MessageRow = styled.div<{ $isUser: boolean }>`
  display: flex;
  justify-content: ${({ $isUser }) => ($isUser ? 'flex-end' : 'flex-start')};
  margin-bottom: 1rem;
`;

export const MessageContentWrapper = styled.div<{ $isUser: boolean }>`
  display: flex;
  max-width: 80%;
  ${({ $isUser }) =>
    $isUser &&
    css`
      flex-direction: row-reverse;
    `}
`;

export const Bubble = styled.div<{ $isUser: boolean }>`
  font-family: Manrope, sans-serif;
  border-radius: 8px;
  padding: ${({ $isUser }) => ($isUser ? '8px 16px' : '8px 0')};
  word-break: break-word;
  background: ${({ $isUser }) =>
    $isUser ? ({ theme }) => theme.colors.background.interactive.secondary.default : 'none'};
  color: #111827;

  p {
    margin-bottom: 0;
  }

  ul,
  ol {
    list-style-type: disc;
    padding-left: 20px;
    margin: 16px;
  }

  /* Estilos para tabla */
  table {
    width: 125%;
    border-collapse: collapse;
    margin-top: 0.5rem;
    background-color: #ffffff;
    border-radius: 0.75rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    font-size: 12px;
  }

  thead tr {
    background-color: #f9fafb;
  }

  th,
  td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
    color: #333;
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: normal;
  }

  th {
    background-color: #f9fafb;
    font-weight: 600;
  }

  tr:last-child td {
    border-bottom: none;
  }
`;

export const Timestamp = styled.div<{ $isUser: boolean }>`
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
  text-align: ${({ $isUser }) => ($isUser ? 'right' : 'left')};
`;
