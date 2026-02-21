const path = require('path');

const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const ReactRefreshPlugin = require('@pmmmwh/react-refresh-webpack-plugin');
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

const moduleFederationConfig = require('./module.federation.config');

const env = process.env;
const envKeys = Object.keys(env)
  .filter(key => key.startsWith('REACT_APP'))
  .reduce((prev, next) => {
    prev[next] = JSON.stringify(env[next]);
    return prev;
  }, {});

const publicStaticPath =
  process.env.STATIC_BASE_URL && process.env.STATIC_BASE_URL.toUpperCase() !== 'NA' ? process.env.STATIC_BASE_URL : '/';

module.exports = (_, argv = {}) => {
  const isEnvDevelopment = argv.mode !== 'production';

  return {
    entry: path.resolve('src/index.tsx'),
    mode: isEnvDevelopment ? 'development' : 'production',
    devtool: isEnvDevelopment ? 'inline-source-map' : 'source-map',
    output: {
      path: path.resolve('build'),
      filename: '[name].[fullhash].js',
      chunkFilename: '[name].[contenthash].js',
      uniqueName: 'shell',
      publicPath: publicStaticPath,
      clean: true,
    },
    devServer: {
      port: process.env.PORT_NUMBER,
      static: {
        directory: path.resolve(__dirname, 'public'),
      },
      historyApiFallback: {
        index: publicStaticPath,
      },
      allowedHosts: 'all',
      server: env.REACT_APP_SERVER_PROTOCOL,
      hot: true,
      compress: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
        'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization',
      },
    },
    resolve: {
      extensions: ['.js', '.mjs', '.jsx', '.ts', '.tsx', '.jpg', 'png', 'jpeg'],
      alias: {
        events: 'events',
      },
      plugins: [new TsconfigPathsPlugin()],
    },
    plugins: [
      isEnvDevelopment && new ReactRefreshPlugin(),
      new HtmlWebpackPlugin({
        inject: true,
        template: path.resolve('public/index.html'),
      }),
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
        ],
      }),
    ].filter(Boolean),
    module: {
      rules: [
        {
          test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/],
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: 'images/[name].[hash:8].[ext]',
          },
        },
        {
          test: [/\.svg$/i],
          issuer: /\.[jt]sx?$/,
          use: [
            {
              loader: '@svgr/webpack',
              options: {
                icon: true,
              },
            },
            {
              loader: 'file-loader',
              options: {
                name: 'images/[name].[hash:8].[ext]',
              },
            },
          ],
        },
        {
          test: /\.([jt]sx?)?$/,
          use: 'swc-loader',
          exclude: /node_modules/,
        },
        {
          test: [/\.(woff|woff2|ttf)?$/],
          use: {
            loader: 'file-loader',
            options: {
              name: 'fonts/[name].[ext]',
            },
          },
        },
        {
          test: [/\.css$/],
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    optimization: {
      moduleIds: 'size',
      minimize: !isEnvDevelopment,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            ecma: 5,
            mangle: {
              safari10: true,
            },
            output: {
              comments: false,
            },
          },
        }),
      ],
    },
    experiments: {
      topLevelAwait: true,
    },
  };
};
