/**
 * POST /api/tasks - Placeholder for future HTTP endpoint
 *
 * **Context:** Phase 06-03
 *
 * Currently, task creation uses Server Actions (see @/app/actions/tasks).
 * This file exists for future HTTP endpoint implementation if needed.
 */

import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  return NextResponse.json(
    { message: "Use Server Actions instead. See @/app/actions/tasks" },
    { status: 501 }
  )
}
