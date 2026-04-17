import { z } from "zod";

export const resetPasswordSchema = z.object({
  token: z.string().min(1, "Token is required."),
  new_password: z
    .string()
    .min(8, "Password must contain at least 8 characters.")
    .max(25, "Password must contain at most 25 characters."),
});

export type ResetPasswordSchemaValues = z.infer<typeof resetPasswordSchema>;