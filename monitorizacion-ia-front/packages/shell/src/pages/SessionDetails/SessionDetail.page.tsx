/* istanbul ignore file */
import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@internal-channels-components/button';
import { Icon } from '@internal-channels-components/icon';

import ChatPage from '#/shell/pages/Chat/Chat.page';
import { getRoutePath } from '#/shell/router/router.config';

import { Header, Main } from './SessionDetail.styles';

const SessionDetailPage = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    // setLoading(true);
    // try {
    //   const data = await sesionService.getSesiones(queryParams.toString());
    // } catch (e) {
    //   const items = sesiones_mock;
    //   setSesiones(items);
    // } finally {
    //   setLoading(false);
    // }
  };

  return (
    <Main>
      <Header>
        <Button
          label="Volver"
          icon={<Icon name="interfaceArrowsButtonLeft" width={20} height={20} color="white"></Icon>}
          onClick={() => {
            navigate(getRoutePath('sessionList'));
          }}></Button>
        <p>
          Detalles de la sesión <b>{id}</b>
        </p>
      </Header>

      <ChatPage idSesion={id}></ChatPage>
    </Main>
  );
};

export const element = <SessionDetailPage />;
