import { z } from "zod";

export const registerSchema = z.object({
  email: z.email("Please enter a valid email address."),
  password: z
    .string()
    .min(8, "Password must contain at least 8 characters.")
    .max(25, "Password must contain at most 25 characters."),
  user_name: z
    .string()
    .min(1, "Name is required.")
    .max(255, "Name must contain at most 255 characters."),
});

export type RegisterSchemaValues = z.infer<typeof registerSchema>;