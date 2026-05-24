import {
  fetchActiveRuns,
  fetchProjectActivity,
  fetchProjectDecisions,
  fetchProjectList,
  fetchProjectOverview,
  fetchProjectTimeSummary,
  fetchProjectTasks,
  fetchProjectTokenUsage,
  fetchTaskContextProjection,
  fetchTaskDependencies,
  fetchTaskDoctrineProjection,
} from '@/lib/project-state-api'
import { ProjectStateLiveShell } from '@/components/project-state/ProjectStateLiveShell'

export const dynamic = 'force-dynamic'

interface ProjectStatePageProps {
  searchParams?: Promise<{
    project?: string
    task?: string
  }>
}

export default async function ProjectStatePage({
  searchParams,
}: ProjectStatePageProps) {
  const params = (await searchParams) ?? {}

  const projects = await fetchProjectList()
  const selectedProjectId = params.project ?? projects[0]?.project_id ?? null

  if (!selectedProjectId) {
    return (
      <ProjectStateLiveShell
        projects={projects}
        selectedProjectId={null}
        selectedTaskId={null}
        overview={null}
        timeSummary={null}
        tasks={[]}
        dependencies={[]}
        runs={[]}
        decisions={[]}
        activity={[]}
        tokenUsage={[]}
        contextProjection={null}
        doctrineProjection={null}
      />
    )
  }


  const [overview, timeSummary, tasks, runs, decisions, activity, tokenUsage] = await Promise.all([
    fetchProjectOverview(selectedProjectId),
    fetchProjectTimeSummary(selectedProjectId),
    fetchProjectTasks(selectedProjectId),
    fetchActiveRuns(selectedProjectId),
    fetchProjectDecisions(selectedProjectId),
    fetchProjectActivity(selectedProjectId),
    fetchProjectTokenUsage(selectedProjectId),
  ])

  const selectedTaskId = params.task ?? tasks[0]?.task_id ?? null

  let dependencies = [] as Awaited<ReturnType<typeof fetchTaskDependencies>>
  let contextProjection = null as Awaited<ReturnType<typeof fetchTaskContextProjection>> | null
  let doctrineProjection = null as Awaited<ReturnType<typeof fetchTaskDoctrineProjection>> | null

  if (selectedTaskId) {
    ;[dependencies, contextProjection, doctrineProjection] = await Promise.all([
      fetchTaskDependencies(selectedProjectId, selectedTaskId),
      fetchTaskContextProjection(selectedProjectId, selectedTaskId),
      fetchTaskDoctrineProjection(selectedProjectId, selectedTaskId),
    ])
  }

  return (
    <ProjectStateLiveShell
      projectId={selectedProjectId}
      projects={projects}
      selectedProjectId={selectedProjectId}
      selectedTaskId={selectedTaskId}
      overview={overview}
      timeSummary={timeSummary}
      tasks={tasks}
      dependencies={dependencies}
      runs={runs}
      decisions={decisions}
      activity={activity}
      tokenUsage={tokenUsage}
      contextProjection={contextProjection}
      doctrineProjection={doctrineProjection}
    />
  )
}
