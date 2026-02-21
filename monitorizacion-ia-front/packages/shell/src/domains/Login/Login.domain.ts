import { storageSession } from '@internal-channels-components/storage';
import { ErrorHandler, ErrorHandlerProps } from '@internal-channels-components/error-handler';

export interface ILogin {
  username: string;
  pwd: string;
}

export type ActionDataProps = {
  errors?: { username?: string; pin?: string; login?: string };
  userData: { username?: string; pin?: string };
};

export const handleThrowErrors = (error: ErrorHandlerProps) => {
  throw new ErrorHandler(error);
};

export const handleMessageErrors = (error: ErrorHandlerProps) => {
  const errors: ActionDataProps['errors'] = {};
  errors.pin = `errorMessages.signIn.codes.${error.code}`;

  return errors;
};

export const validateForm = (formData: ILogin) => {
  const errors: ActionDataProps['errors'] = {};

  if (!formData.username || typeof formData.username !== 'string') {
    errors.username = 'errorMessages.invalidUsername';
  }

  if (!formData.pwd || typeof formData.pwd !== 'string' || formData.pwd.length < 6) {
    errors.pin = 'errorMessages.invalidPin';
  }

  return errors;
};

export const callAuthentication = async ({ username }: Partial<ILogin>) => {
  if (storageSession !== undefined) {
    storageSession.setItem('username', username!);
    await continueOauthSession();
  }
};

async function continueOauthSession() {}
