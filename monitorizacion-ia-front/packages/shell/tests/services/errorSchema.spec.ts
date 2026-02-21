import { errorSchema } from './../../src/services/errorSchema';

describe('ErrorSchema', () => {
  test('should export errorSchema', () => {
    expect(errorSchema).toBeDefined();
    expect(
      errorSchema.parse({
        codigoError: '1',
        mensajeError: '2',
      }),
    ).toEqual({
      codigoError: '1',
      mensajeError: '2',
    });
  });
});
