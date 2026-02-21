export default {
  apiHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://univiapru.unicajabanco.es/apis-nopr/externo/desa-unicaja`,
  wasHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://univiapru.unicajabanco.es/services/rest`,
  apiInternalHost: `${process.env.REACT_APP_SERVER_PROTOCOL}://apis-nopr.unicajabanco.es/externo/desa-unicaja`,
  login: {
    oauthURI: '/banca-digital-desa/oauth2',
    oauthRedirect: `${process.env.REACT_APP_SERVER_PROTOCOL}://featurepru20.unicajabanco.es/access`,
    oauthConfirmationRedirect: `${process.env.REACT_APP_SERVER_PROTOCOL}://featurepru20.unicajabanco.es/login?original-url=`,
    clientId: '0c3132ffafffcf967786a17d95bafa5b',
    scope: 'openid+BD',
  },
} as const;
