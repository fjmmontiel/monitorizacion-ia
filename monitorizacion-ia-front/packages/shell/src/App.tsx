/* istanbul ignore file */
import { RouterProvider } from 'react-router-dom';

import { router } from './router/router';
import { useLogoutOnWindowClose } from './hooks/useLogoutOnWindowClose';

function App() {
  useLogoutOnWindowClose();
  return <RouterProvider router={router} />;
}

export default App;
