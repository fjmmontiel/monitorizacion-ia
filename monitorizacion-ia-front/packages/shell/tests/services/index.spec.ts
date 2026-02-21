import { services } from '../../src/services';
import '@testing-library/jest-dom';

jest.mock('@internal-channels-components/http', () => {
  return {
    __esModule: true,
    Http: jest.fn().mockImplementation(() => {
      return {
        get: () => jest.fn(),
        post: () => jest.fn(),
        setBaseUrl: jest.fn(),
      };
    }),
  };
});

describe('Services', () => {
  test('should export services', () => {
    expect(services).toBeDefined();
  });
});
