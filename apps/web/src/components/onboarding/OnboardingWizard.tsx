'use client';

import { useEffect } from 'react';
import { useOnboardingStore, OnboardingStep } from '@/stores/onboardingStore';
import { WelcomeStep } from './WelcomeStep';
import { CompanyAdapterStep } from './CompanyAdapterStep';
import { ValidationStep } from './ValidationStep';
import { CompletionStep } from './CompletionStep';
import { cn } from '@/lib/utils';

const STEPS: { key: OnboardingStep; label: string }[] = [
  { key: 'welcome', label: 'Welcome' },
  { key: 'company-adapter', label: 'Setup' },
  { key: 'validation', label: 'Validation' },
  { key: 'complete', label: 'Complete' },
];

export function OnboardingWizard() {
  const { currentStep, startOnboarding } = useOnboardingStore();

  useEffect(() => {
    startOnboarding();
  }, [startOnboarding]);

  const currentStepIndex = STEPS.findIndex((step) => step.key === currentStep);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {STEPS.slice(0, 3).map((step, index) => (
              <div key={step.key} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-colors',
                      index <= currentStepIndex
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground'
                    )}
                  >
                    {index < currentStepIndex ? '✓' : index + 1}
                  </div>
                  <span
                    className={cn(
                      'text-xs mt-2 text-center',
                      index <= currentStepIndex
                        ? 'text-foreground'
                        : 'text-muted-foreground'
                    )}
                  >
                    {step.label}
                  </span>
                </div>
                {index < STEPS.slice(0, 3).length - 1 && (
                  <div
                    className={cn(
                      'flex-1 h-1 mx-2 transition-colors',
                      index < currentStepIndex ? 'bg-primary' : 'bg-muted'
                    )}
                  />
                )}
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-muted-foreground">
            Step {currentStepIndex + 1} of 3
          </p>
        </div>

        {/* Step Content */}
        <div className="bg-background rounded-lg shadow-xl border p-8">
          {currentStep === 'welcome' && <WelcomeStep />}
          {currentStep === 'company-adapter' && <CompanyAdapterStep />}
          {currentStep === 'validation' && <ValidationStep />}
          {currentStep === 'complete' && <CompletionStep />}
        </div>

        {/* Skip Button */}
        {currentStep !== 'complete' && (
          <button
            onClick={() => useOnboardingStore.getState().skipOnboarding()}
            className="mt-4 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Skip onboarding
          </button>
        )}
      </div>
    </div>
  );
}
