import { z } from "zod";

export const loginSchema = z.object({
  email: z.email("Please enter a valid email address."),
  password: z
    .string()
    .min(8, "Password must contain at least 8 characters.")
    .max(25, "Password must contain at most 25 characters."),
});

export type LoginSchemaValues = z.infer<typeof loginSchema>;