import { readFileSync } from "node:fs"
import path from "node:path"

import { describe, expect, it } from "vitest"

import {
  toDispatchTaskRequest,
  type DispatchTaskRequest,
  type DispatchTaskResponse,
} from "@/proto/brain_runtime"

function readProtoContract(): string {
  const protoPath = path.resolve(
    process.cwd(),
    "..",
    "..",
    "proto",
    "mastermind",
    "v1",
    "brain_runtime.proto",
  )
  return readFileSync(protoPath, "utf8")
}

describe("brain_runtime proto shim", () => {
  it("keeps DispatchTaskRequest aligned with the proto contract", () => {
    const proto = readProtoContract()
    const request: DispatchTaskRequest = toDispatchTaskRequest("brief", "user-1")

    expect(proto).toContain("rpc DispatchTask(DispatchTaskRequest) returns (DispatchTaskResponse);")
    expect(proto).toContain("string brief = 1;")
    expect(proto).toContain("string user_id = 2;")
    expect(proto).toContain("string flow = 3;")

    expect(request).toEqual({
      brief: "brief",
      userId: "user-1",
      flow: "auto",
    })
  })

  it("keeps DispatchTaskResponse field intent aligned with the proto contract", () => {
    const proto = readProtoContract()
    const response: DispatchTaskResponse = {
      taskId: "task-1",
      status: "pending",
      acceptedAtUnixMs: 123,
    }

    expect(proto).toContain("string task_id = 1;")
    expect(proto).toContain("string status = 2;")
    expect(proto).toContain("int64 accepted_at_unix_ms = 3;")

    expect(response.taskId).toBe("task-1")
    expect(response.status).toBe("pending")
    expect(response.acceptedAtUnixMs).toBe(123)
  })
})
