export default {
  apiHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://localhost:${process.env.REACT_APP_MOCK_PORT_NUMBER}`,
  apiInternalHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://localhost:${process.env.REACT_APP_MOCK_PORT_NUMBER}`,
  wasHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://localhost:${process.env.REACT_APP_MOCK_PORT_NUMBER}`,
  login: {
    oauthURI: '',
    oauthRedirect: `${process.env.REACT_APP_SERVER_PROTOCOL}://localhost:${process.env.PORT_NUMBER}/access`,
    oauthConfirmationRedirect: `${process.env.REACT_APP_SERVER_PROTOCOL}://localhost:${process.env.PORT_NUMBER}/login?original-url=`,
    clientId: 'clientDummy1234',
    scope: 'openid+BD',
  },
} as const;
