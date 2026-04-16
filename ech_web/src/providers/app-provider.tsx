"use client";

import { ReactNode } from "react";

// import { AuthProvider } from "@/providers/auth-provider";
import { QueryProvider } from "@/providers/query-provider";
import { ToastProvider } from "@/providers/toast-provider";

// type AppProviderProps = {
//   children: ReactNode;
// };

// export function AppProvider({ children }: AppProviderProps) {
//   return (
//     <QueryProvider>
//       <AuthProvider>
//         <ToastProvider>{children}</ToastProvider>
//       </AuthProvider>
//     </QueryProvider>
//   );
// }