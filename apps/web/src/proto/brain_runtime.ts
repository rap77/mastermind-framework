// Generated proto types for TypeScript
// TODO: Generate from proto/mastermind/v1/brain_runtime.proto using ts-proto
// Setup blocker: buf CLI not available, documented in velocity-baseline.md

export interface DispatchTaskRequest {
  brief: string;
  userId: string;
  flow: string;
}

export interface DispatchTaskResponse {
  taskId: string;
  status: string;
  acceptedAtUnixMs: number;
}

// Helper function to convert snake_case to camelCase for TypeScript
export function toDispatchTaskRequest(brief: string, userId: string, flow: string = "auto"): DispatchTaskRequest {
  return {
    brief,
    userId,
    flow,
  };
}
