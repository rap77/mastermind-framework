import type { ReactNode } from "react";

/**
 * Protected route layout placeholder
 * AuthGuardLayout will be implemented in Plan 05-02
 */
export default function ProtectedLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      {/* TODO: Add AuthGuard in Plan 05-02 */}
      {children}
    </div>
  );
}
