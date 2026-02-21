import { z } from 'zod';

export const errorSchema = z.object({
  codigoError: z.string(),
  mensajeError: z.string(),
});
