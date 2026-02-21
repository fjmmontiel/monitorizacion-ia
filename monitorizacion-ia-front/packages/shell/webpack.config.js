const path = require('path');

const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

const { getConfig, envKeys } = require('../../webpack/webpack.config');

const moduleFederationConfig = require('./module.federation.config');

const publicStaticPath =
  process.env.STATIC_BASE_URL && process.env.STATIC_BASE_URL.toUpperCase() !== 'NA' ? process.env.STATIC_BASE_URL : '/';

// eslint-disable-next-line no-unused-vars
module.exports = (_, argsv) => {
  const config = getConfig(_, argsv);

  return {
    ...config,
    entry: path.resolve('src/index.tsx'),
    output: {
      ...config.output,
      uniqueName: 'shell',
      publicPath: publicStaticPath,
    },
    devServer: {
      ...config.devServer,
      port: process.env.PORT_NUMBER,
      static: {
        directory: path.resolve(__dirname, 'public'),
      },
      historyApiFallback: {
        index: publicStaticPath,
      },
    },
    resolve: {
      ...config.resolve,
      alias: {
        ...config.resolve.alias,
      },
      plugins: [...config.resolve.plugins, new TsconfigPathsPlugin()],
    },
    plugins: [
      ...config.plugins,
      new ModuleFederationPlugin(moduleFederationConfig.pluginConfig),
      new webpack.DefinePlugin({
        'process.env': {
          ...envKeys,
          REMOTES: JSON.stringify(moduleFederationConfig.remotes),
        },
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve('public'),
            to: '.',
            toType: 'dir',
            globOptions: {
              ignore: ['**/index.html'],
            },
          },
        ].filter(Boolean),
      }),
    ].filter(Boolean),
  };
};
