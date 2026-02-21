/* istanbul ignore file */
import { defineConfig } from 'cypress';

import webpackConfig from './webpack.config';

export default defineConfig({
  video: false,
  reporter: '../../node_modules/mochawesome',
  reporterOptions: {
    reportDir: 'cypress/report',
    overwrite: false,
    html: false,
    json: true,
  },
  component: {
    viewportWidth: 1024,
    viewportHeight: 640,
    chromeWebSecurity: false,
    devServer: {
      framework: 'react',
      bundler: 'webpack',
      webpackConfig: async () => {
        const customConfig = webpackConfig();
        customConfig.devServer.server = 'http'; // Cypress component test runs in http mode only
        return customConfig;
      },
    },
    specPattern: 'cypress/functional/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.ts',
    indexHtmlFile: 'cypress/support/component-index.html',
    fixturesFolder: 'cypress/fixtures',
    screenshotsFolder: 'cypress/screenshots/functional',
    videosFolder: 'cypress/videos/functional',
  },
});
