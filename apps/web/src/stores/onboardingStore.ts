import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type OnboardingStep = 'welcome' | 'company-adapter' | 'validation' | 'complete';

export interface CompanyData {
  name: string;
  industry: string;
  goal: string;
}

export interface AdapterConfig {
  provider: 'openai' | 'anthropic' | 'local';
  apiKey?: string;
  baseUrl?: string;
}

interface OnboardingState {
  currentStep: OnboardingStep;
  companyData: CompanyData;
  adapterConfig: AdapterConfig;
  hasCompletedOnboarding: boolean;
  isSubmitting: boolean;
  error: string | null;

  // Analytics per Brain #7 requirement
  startTime: number | null;
  stepTimes: Record<OnboardingStep, number>;
}

interface OnboardingActions {
  setStep: (step: OnboardingStep) => void;
  nextStep: () => void;
  prevStep: () => void;
  setCompanyData: (data: Partial<CompanyData>) => void;
  setAdapterConfig: (config: Partial<AdapterConfig>) => void;
  completeOnboarding: () => void;
  skipOnboarding: () => void;
  reset: () => void;
  setError: (error: string | null) => void;
  startOnboarding: () => void;
  recordStepTime: (step: OnboardingStep) => void;
}

const INITIAL_STATE: OnboardingState = {
  currentStep: 'welcome',
  companyData: {
    name: '',
    industry: '',
    goal: '',
  },
  adapterConfig: {
    provider: 'openai',
    apiKey: '',
    baseUrl: '',
  },
  hasCompletedOnboarding: false,
  isSubmitting: false,
  error: null,
  startTime: null,
  stepTimes: {
    welcome: 0,
    'company-adapter': 0,
    validation: 0,
    complete: 0,
  },
};

export const useOnboardingStore = create<OnboardingState & OnboardingActions>()(
  persist(
    (set, get) => ({
      ...INITIAL_STATE,

      setStep: (step) => set({ currentStep: step }),

      nextStep: () => {
        const { currentStep } = get();
        const steps: OnboardingStep[] = ['welcome', 'company-adapter', 'validation', 'complete'];
        const currentIndex = steps.indexOf(currentStep);

        if (currentIndex < steps.length - 1) {
          // Record time spent on current step
          get().recordStepTime(currentStep);

          set({ currentStep: steps[currentIndex + 1] });
        }
      },

      prevStep: () => {
        const { currentStep } = get();
        const steps: OnboardingStep[] = ['welcome', 'company-adapter', 'validation', 'complete'];
        const currentIndex = steps.indexOf(currentStep);

        if (currentIndex > 0) {
          set({ currentStep: steps[currentIndex - 1] });
        }
      },

      setCompanyData: (data) =>
        set((state) => ({
          companyData: { ...state.companyData, ...data },
        })),

      setAdapterConfig: (config) =>
        set((state) => ({
          adapterConfig: { ...state.adapterConfig, ...config },
        })),

      completeOnboarding: () => {
        const { recordStepTime } = get();
        recordStepTime('complete');

        // Track completion event for analytics per Brain #7
        const totalTime = Date.now() - (get().startTime || Date.now());
        console.log(`Onboarding completed in ${totalTime}ms`);

        set({
          hasCompletedOnboarding: true,
          currentStep: 'complete',
          isSubmitting: false,
        });
      },

      skipOnboarding: () => {
        set({
          hasCompletedOnboarding: true,
          currentStep: 'complete',
        });
      },

      reset: () => set(INITIAL_STATE),

      setError: (error) => set({ error }),

      startOnboarding: () => {
        set({ startTime: Date.now() });
      },

      recordStepTime: (step) => {
        const now = Date.now();
        const startTime = get().startTime || now;

        set((state) => ({
          stepTimes: {
            ...state.stepTimes,
            [step]: now - startTime,
          },
        }));
      },
    }),
    {
      name: 'mastermind-onboarding',
      partialize: (state) => ({
        hasCompletedOnboarding: state.hasCompletedOnboarding,
        companyData: state.companyData,
        adapterConfig: state.adapterConfig,
      }),
    }
  )
);
