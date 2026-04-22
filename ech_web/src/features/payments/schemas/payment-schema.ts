import { z } from "zod";

const paymentMethodValues = [
  "credit_card",
  "debit_card",
  "pix",
  "bank_slip",
  "wallet",
] as const;

export const createPaymentSchema = z.object({
  order_id: z.string().uuid("Invalid order id"),
  method: z.enum(paymentMethodValues, {
    message: "Payment method is required",
  }),
  payment_reference: z.string().optional(),
});

export type CreatePaymentSchemaValues = z.infer<typeof createPaymentSchema>;

export const createRefundSchema = z.object({
  amount: z.coerce
    .number()
    .refine((value) => Number.isFinite(value), {
      message: "Amount must be a number",
    })
    .positive("Amount must be greater than 0"),
  reason: z.string().min(3, "Reason is required"),
});

export type CreateRefundSchemaValues = z.infer<typeof createRefundSchema>;