const path = require('path');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const ReactRefreshPlugin = require('@pmmmwh/react-refresh-webpack-plugin');

const env = process.env;
module.exports.envKeys = Object.keys(env)
  .filter(e => e.startsWith('REACT_APP'))
  .reduce((prev, next) => {
    prev[next] = JSON.stringify(env[next]);
    return prev;
  }, {});

module.exports.getConfig = (_, { mode } = {}) => {
  const isEnvDevelopment = mode !== 'production';

  return {
    entry: path.resolve('src/index.tsx'),
    mode: !isEnvDevelopment ? 'production' : 'development',
    devtool: isEnvDevelopment ? 'inline-source-map' : 'source-map',
    output: {
      path: path.resolve('build'),
      filename: '[name].[fullhash].js',
      chunkFilename: '[name].[contenthash].js',
    },
    devServer: {
      static: {
        directory: path.resolve(__dirname, './public'),
      },
      historyApiFallback: true,
      allowedHosts: 'all',
      server: env.REACT_APP_SERVER_PROTOCOL,
      hot: true,
      compress: true, // enable gzip compression
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
      plugins: [],
    },
    plugins: [
      isEnvDevelopment && new ReactRefreshPlugin(),
      new HtmlWebpackPlugin({
        inject: true,
        template: path.resolve('public/index.html'),
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
