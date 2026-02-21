/* istanbul ignore file */
const deps = require('./package.json').dependencies;

// These dependencies are excluded to be shared as they causes issues when launching MFEs
const excludeShared = [];

const sharedDeps = Object.fromEntries(
  Object.entries(deps).filter(([key]) => !excludeShared.some(e => new RegExp(e, 'g').test(key))),
);

module.exports = {
  pluginConfig: {
    name: 'app_shell',
    filename: 'remoteEntry.js',
    exposes: {},
    shared: {
      ...sharedDeps,
      react: {
        singleton: true,
        requiredVersion: deps.react,
      },
      'react-dom': {
        singleton: true,
        requiredVersion: deps['react-dom'],
      },
    },
  },
  remotes: {},
};
