/* istanbul ignore file */
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <>
      <h2>Nothing to see here!</h2>
      <p>
        <Link to="/">Go to the home page</Link>
      </p>
    </>
  );
};

export const element = <NotFoundPage />;
