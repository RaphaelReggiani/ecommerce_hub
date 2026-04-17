import { z } from "zod";

export const profileSchema = z.object({
  user_name: z
    .string()
    .min(1, "Name is required.")
    .max(255, "Name must contain at most 255 characters."),
  user_phone: z.string().max(15, "Phone must contain at most 15 characters.").optional(),
  user_country: z.string().max(50, "Country must contain at most 50 characters.").optional(),
  user_state: z.string().max(50, "State must contain at most 50 characters.").optional(),
  user_address: z.string().max(50, "Address must contain at most 50 characters.").optional(),
  user_age: z
    .number()
    .min(18, "You must be at least 18 years old.")
    .max(95, "Age must be at most 95.")
    .nullable()
    .optional(),
});

export type ProfileSchemaValues = z.infer<typeof profileSchema>;