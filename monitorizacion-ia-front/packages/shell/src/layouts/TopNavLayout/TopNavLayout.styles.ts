import styled from 'styled-components';

export const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  padding: 16px 40px;
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

  @media (max-width: 1024px) {
    padding: 16px 24px;
  }

  @media (max-width: 768px) {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }
`;

export const HeaderContent = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  .desktop-user-profile {
    display: none;
  }

  .mobile-user-profile {
    display: block;
  }

  @media (min-width: 769px) {
    .desktop-user-profile {
      display: block;
    }

    .mobile-user-profile {
      display: none;
    }
  }

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
`;

export const TopSection = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  @media (min-width: 769px) {
    width: auto;
  }
`;

export const LogoContainer = styled.div`
  display: flex;
  align-items: center;

  img {
    height: 40px;

    @media (max-width: 480px) {
      height: 32px;
    }
  }
`;

export const MainContent = styled.main`
  flex: 1;
  padding: 0;

  /* @media (max-width: 768px) {
    padding-top: 20px;
  }

  @media (min-width: 769px) {
    padding: 0 20px 20px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  } */
`;
