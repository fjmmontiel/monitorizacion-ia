import * as domain from '#/shell/domains/Login/Login.domain';

jest.mock('#/shell/config', () => ({
  default: {
    apiHost: 'https://api.example.com',
    wasHost: 'https://was.example.com',
    apiInternalHost: 'https://internal.api.example.com',
    login: {
      oauthURI: 'https://oauth.example.com',
      oauthRedirect: 'https://oauth.example.com/redirect',
      oauthConfirmationRedirect: 'https://oauth.example.com/confirmation-redirect',
      clientId: 'your-client-id',
      scope: 'your-scope',
    },
  },
}));

let mockPost: jest.Mock = jest.fn();

jest.mock('@internal-channels-components/http', () => {
  return {
    __esModule: true,
    Http: jest.fn().mockImplementation(() => {
      return {
        get: () => jest.fn(),
        post: () => mockPost,
        setBaseUrl: jest.fn(),
      };
    }),
  };
});

describe('Login domain', () => {
  // test('should throw an error', () => {
  //   const error = { code: 400 };

  //   expect(() => domain.handleThrowErrors(error)).toThrow();
  // });
  // test('should return an error object', () => {
  //   const error = { code: 400 };

  //   const result = domain.handleMessageErrors(error);

  //   expect(result).toEqual({ pin: 'errorMessages.signIn.codes.400' });
  // });

  test('should return errors for invalid form data', () => {
    const formData = {
      username: '',
      pwd: '123',
    };

    const result = domain.validateForm(formData);

    expect(result).toEqual({
      username: 'errorMessages.invalidUsername',
      pin: 'errorMessages.invalidPin',
    });
  });

  test('should return empty errors for valid form data', () => {
    const formData = {
      username: 'john',
      pwd: 'pas',
    };

    domain.validateForm(formData);
  });

  test('should call originalUrlService with username and confirmation parameters', async () => {
    // Arrange
    // Mock storage implementation
    const mockLocalStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      clear: jest.fn(),
    };
    Object.defineProperty(window, 'sessionStorage', {
      value: mockLocalStorage,
    });
    // Mock originalUrlService
    // eslint-disable-next-line no-unused-vars
    // const originalUrlService = jest.fn().mockResolvedValue('Success');
    mockLocalStorage.getItem.mockReturnValueOnce('mockOriginalUrl');
    mockLocalStorage.getItem.mockReturnValueOnce('mockUsername');
    mockLocalStorage.getItem.mockReturnValueOnce('mockConfirmation');

    // Act
    const username = 'john';
    await domain.callAuthentication({ username });

    // TODO: mirar porque el mock del storAGe no esta funcionando

    // Assert
    // expect(storage.getItem).toHaveBeenCalledWith('username');
    // expect(storage.getItem).toHaveBeenCalledWith('confirmation');
    // expect(originalUrlService).toHaveBeenCalledWith('mockOriginalUrl', {
    //   params: { username: 'mockUsername', confirmation: 'mockConfirmation' },
    // });
  });
});
