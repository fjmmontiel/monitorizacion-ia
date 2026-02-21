export default {
  preset: '@architecture-components/test-config',
  transform: {
    '^.+\\.(ts|tsx|js|jsx|mjs)$': ['@swc/jest', { module: { type: 'commonjs' } }],
    'node_modules/@architecture-components/.+\\.(j|t)sx?$': ['@swc/jest', { module: { type: 'commonjs' } }],
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@architecture-components|swiper|ssr-window|dom7|react-pdf|react-popper-tooltip)/)',
  ],
  moduleNameMapper: {
    '#/shell/(.*)': '<rootDir>/packages/shell/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.svg$': '<rootDir>/__mocks__/svgMock.js',
  },
};
