import { defineConfig } from 'cypress';

export default defineConfig({
  video: false,
  reporter: '../node_modules/mochawesome',
  reporterOptions: {
    reportDir: 'report',
    overwrite: false,
    html: false,
    json: true,
  },
  retries: {
    runMode: 2,
    openMode: 0,
  },
  chromeWebSecurity: false,
  e2e: {
    video: false,
    screenshotOnRunFailure: false,
    experimentalMemoryManagement: true,
    experimentalRunAllSpecs: true,
    defaultCommandTimeout: 12000,
    pageLoadTimeout: 110000,
    viewportWidth: 1280,
    baseUrl: 'http://localhost:3000',
    specPattern: './e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: './support/e2e.ts',
    fixturesFolder: './fixtures',
    screenshotsFolder: './screenshots/e2e',
    videosFolder: './videos/e2e',
  },
});
