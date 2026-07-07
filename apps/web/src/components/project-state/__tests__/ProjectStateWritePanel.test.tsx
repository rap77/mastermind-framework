import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ProjectStateWritePanel } from '../ProjectStateWritePanel'

const refreshMock = vi.fn()
const updateProjectDoctrineMock = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    refresh: refreshMock,
  }),
}))

vi.mock('@/app/actions/project-state', () => ({
  createProjectCheckpoint: vi.fn(),
  createProjectDecision: vi.fn(),
  updateProjectDoctrine: (...args: unknown[]) => updateProjectDoctrineMock(...args),
  updateProjectTaskStatus: vi.fn(),
}))

vi.mock('@/lib/toast', () => ({
  toastError: vi.fn(),
  toastSuccess: vi.fn(),
}))

beforeEach(() => {
  vi.clearAllMocks()
})

const baseProps = {
  selectedProjectId: 'project-1',
  selectedTaskId: null,
  runs: [],
  contextProjection: null,
  doctrineProjection: {
    methodology: {
      active: 'AI-DLC',
      reason: 'Need the full discovery-to-delivery loop.',
      required_phases: ['discovery', 'design', 'implementation', 'verification'],
    },
    policies: [],
    mandatory_rules: [],
    quality_gates: [],
    architecture_constraints: [],
  },
  policyOptions: [
    {
      capability_id: 'policy-clean-code',
      label: 'Clean Code',
      summary: 'Keep the implementation readable, small, and easy to change.',
      compatible_harnesses: ['execution-default', 'verification-default'],
    },
    {
      capability_id: 'policy-security',
      label: 'Security',
      summary: 'Treat untrusted input as hostile and prefer safe defaults.',
      compatible_harnesses: ['execution-default', 'verification-default'],
    },
    {
      capability_id: 'policy-architecture',
      label: 'Architecture',
      summary: 'Preserve layer boundaries and avoid coupling concerns.',
      compatible_harnesses: ['execution-default', 'verification-default'],
    },
    {
      capability_id: 'policy-naming',
      label: 'Naming',
      summary: 'Use explicit names that reflect intent and scope.',
      compatible_harnesses: ['execution-default', 'verification-default'],
    },
    {
      capability_id: 'policy-testing-discipline',
      label: 'Testing Discipline',
      summary: 'Keep behavior covered with stable, focused tests.',
      compatible_harnesses: ['execution-default', 'verification-default'],
    },
  ],
}

describe('ProjectStateWritePanel', () => {
  it('renders the methodology selector with the active doctrine', () => {
    render(<ProjectStateWritePanel {...baseProps} />)

    expect(screen.getByText('Select methodology')).toBeInTheDocument()
    expect(screen.getByLabelText('Methodology')).toHaveValue('AI-DLC')
    expect(screen.getByLabelText('Reason')).toHaveValue('Need the full discovery-to-delivery loop.')
  })

  it('updates doctrine through the server action', async () => {
    updateProjectDoctrineMock.mockResolvedValue({ success: true })

    render(<ProjectStateWritePanel {...baseProps} />)

    fireEvent.change(screen.getByLabelText('Methodology'), { target: { value: 'SDD' } })
    fireEvent.change(screen.getByLabelText('Reason'), { target: { value: 'Spec-first delivery for this slice.' } })
    fireEvent.click(screen.getByRole('button', { name: /update methodology/i }))

    await waitFor(() => {
      expect(updateProjectDoctrineMock).toHaveBeenCalledWith({
        projectId: 'project-1',
        methodology: 'SDD',
        methodologyReason: 'Spec-first delivery for this slice.',
        requiredPhases: ['discover', 'plan', 'verify'],
        policies: [],
      })
    })
  })

  it('persists selected policies as mandatory doctrine rules', async () => {
    updateProjectDoctrineMock.mockResolvedValue({ success: true })

    render(<ProjectStateWritePanel {...baseProps} />)

    fireEvent.click(screen.getByRole('checkbox', { name: /clean code/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /security/i }))
    fireEvent.click(screen.getByRole('button', { name: /update methodology/i }))

    await waitFor(() => {
      expect(updateProjectDoctrineMock).toHaveBeenCalledWith(
        expect.objectContaining({
          policies: ['policy-clean-code', 'policy-security'],
        })
      )
    })
  })

  it('disables policies incompatible with the selected methodology', () => {
    render(
      <ProjectStateWritePanel
        {...baseProps}
        policyOptions={[
          ...baseProps.policyOptions,
          {
            capability_id: 'policy-review-only',
            label: 'Review Only',
            summary: 'Only valid when review is part of the selected harness set.',
            compatible_harnesses: ['review-default'],
          },
        ]}
      />
    )

    expect(screen.getByLabelText(/review only/i)).toBeDisabled()
  })

  it('preserves custom methodology reason and phases on submit', async () => {
    updateProjectDoctrineMock.mockResolvedValue({ success: true })

    render(
      <ProjectStateWritePanel
        {...baseProps}
        doctrineProjection={{
          ...baseProps.doctrineProjection,
          methodology: {
            active: 'Hybrid-Internal',
            reason: 'Keep the bespoke intake and verify phases.',
            required_phases: ['discover', 'verify'],
          },
        }}
      />
    )

    fireEvent.change(screen.getByLabelText('Reason'), { target: { value: '' } })
    fireEvent.click(screen.getByRole('button', { name: /update methodology/i }))

    await waitFor(() => {
      expect(updateProjectDoctrineMock).toHaveBeenCalledWith({
        projectId: 'project-1',
        methodology: 'Hybrid-Internal',
        methodologyReason: 'Keep the bespoke intake and verify phases.',
        requiredPhases: ['discover', 'verify'],
        policies: [],
      })
    })
  })
})
