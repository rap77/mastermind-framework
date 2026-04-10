'use client';

import { Rocket, Keyboard } from 'lucide-react';
import { useOnboardingStore } from '@/stores/onboardingStore';

export function WelcomeStep() {
  const { nextStep } = useOnboardingStore();

  return (
    <div className="space-y-6">
      {/* Illustration */}
      <div className="flex justify-center">
        <div className="w-32 h-32 bg-primary/10 rounded-full flex items-center justify-center">
          <Rocket className="w-16 h-16 text-primary" />
        </div>
      </div>

      {/* Content */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">
          Welcome to MasterMind
        </h1>
        <p className="text-muted-foreground text-lg">
          Your AI-powered command center for strategic decision-making.
          Let's get you set up in 3 simple steps.
        </p>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-8">
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="font-semibold mb-2">🧠 7 Expert Brains</div>
          <p className="text-sm text-muted-foreground">
            Specialized AI agents for product, UX, design, frontend, backend, QA, and growth
          </p>
        </div>
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="font-semibold mb-2">⚡ Global Search</div>
          <p className="text-sm text-muted-foreground">
            Find commands, brains, and settings instantly with fuzzy search
          </p>
        </div>
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="font-semibold mb-2">📊 Real-time Insights</div>
          <p className="text-sm text-muted-foreground">
            Track costs, monitor performance, and optimize your workflow
          </p>
        </div>
      </div>

      {/* Cmd+K Hint per Plan 17-05 Condition 2 */}
      <div className="bg-accent/50 border border-accent rounded-lg p-4 flex items-center gap-4">
        <Keyboard className="w-8 h-8 text-accent-foreground flex-shrink-0" />
        <div className="flex-1">
          <div className="font-semibold text-accent-foreground">
            Pro Tip: Press ⌘K to search anything
          </div>
          <p className="text-sm text-accent-foreground/80">
            Use Cmd+K (Mac) or Ctrl+K (Windows/Linux) to open the command palette and search across all features.
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center pt-4">
        <button
          onClick={nextStep}
          className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors"
        >
          Get Started →
        </button>
      </div>
    </div>
  );
}
