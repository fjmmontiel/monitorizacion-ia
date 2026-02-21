import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  background: ${({ theme }) => theme.colors.background.static.secondary};
  flex-grow: 1;
  padding: 1rem;
  max-width: 69rem;
  margin: 0 auto;
  width: 100%;
`;

export const Inner = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 69rem;
  margin: 1rem auto;
`;

export const InputContainer = styled.div`
  display: flex;
  align-items: center;
  padding-top: 8px;
  background: transparent;
  position: relative;
`;
export const ButtonSendStyles = styled.div`
  position: absolute;
  right: 7px;
  top: 57%;
  transform: translateY(-50%);
`;
export const ButtonRecordStyles = styled.button`
  position: absolute;
  width: 40px;
  height: 40px;
  right: 60px;
  top: 57%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  &[disabled] {
    opacity: 0.6;
    pointer-events: none;
  }
`;

export const StyledTextArea = styled.textarea`
  flex: 1;
  scrollbar-width: none;
  -ms-overflow-style: none;
  resize: none;
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'm',
    })};
  border-radius: 8px;
  border: 1px solid ${({ theme }) => theme.colors.border.interactive.secondary.default};
  padding: 16px;
  font-size: 14px;
  background: #fff;
  outline: none;
  box-shadow: none;
  padding-right: 96px;
  width: 100%;
`;

export const LoadingStyles = styled.div`
  position: absolute;
  right: 7px;
  top: 57%;
  transform: translateY(-50%);
  .p-progress-spinner {
    width: 40px;
    height: 40px;
  }
`;
