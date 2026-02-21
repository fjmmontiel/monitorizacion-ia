/* istanbul ignore file */
import { useLoaderData } from 'react-router-dom';

const Home = () => {
  const { name } = useLoaderData() as Awaited<ReturnType<typeof loader>>;

  return (
    <>
      <h2>{name}</h2>
    </>
  );
};

export const element = <Home />;

export const loader = () => {
  return {
    name: 'Hello world',
  };
};
