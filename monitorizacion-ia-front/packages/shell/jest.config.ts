export default {
  preset: '@architecture-components/test-config',
  collectCoverageFrom: [
    '**/hooks/**/*.{js,jsx,ts,tsx}',
    '**/components/**/*.{js,jsx,ts,tsx}',
    '**/domains/**/*.{js,jsx,ts,tsx}',
    '**/services/**/*.{js,jsx,ts,tsx}',
    '!**/node_modules/**',
  ],
  transform: {
    '^.+\\.(ts|tsx|js|jsx|mjs)$': ['@swc/jest', { module: { type: 'commonjs' } }],
    'node_modules/@architecture-components/.+\\.(j|t)sx?$': ['@swc/jest', { module: { type: 'commonjs' } }],
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@architecture-components|swiper|ssr-window|dom7|react-pdf|react-popper-tooltip|primereact)/)',
  ],
  moduleNameMapper: {
    '#/shell/(.*)': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.svg$': '<rootDir>/__mocks__/svgMock.js',
  },
};
