'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle2, Sparkles } from 'lucide-react';
import { useOnboardingStore } from '@/stores/onboardingStore';

export function CompletionStep() {
  const router = useRouter();
  const { companyData } = useOnboardingStore();

  useEffect(() => {
    // Auto-redirect after 3 seconds
    const timer = setTimeout(() => {
      router.push('/war-room');
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="space-y-6 text-center">
      {/* Success Icon */}
      <div className="flex justify-center">
        <div className="w-24 h-24 bg-green-500/10 rounded-full flex items-center justify-center">
          <CheckCircle2 className="w-12 h-12 text-green-500" />
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4">
        <div className="flex items-center justify-center gap-2">
          <h1 className="text-3xl font-bold">You&apos;re all set!</h1>
          <Sparkles className="w-8 h-8 text-yellow-500" />
        </div>
        <p className="text-muted-foreground text-lg">
          Welcome to MasterMind, <strong>{companyData.name}</strong>!
        </p>
        <p className="text-sm text-muted-foreground">
          Redirecting to your command center in 3 seconds...
        </p>
      </div>

      {/* Next Steps */}
      <div className="bg-muted/50 rounded-lg p-6 text-left space-y-4">
        <h2 className="font-semibold">What&apos;s next?</h2>
        <ul className="space-y-2 text-sm">
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>
              <strong>Press ⌘K</strong> to open the command palette and explore all features
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>
              <strong>Visit the Nexus</strong> to browse and trigger expert brains
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>
              <strong>Check the Strategy Vault</strong> for planning and prioritization tools
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">✓</span>
            <span>
              <strong>Explore Settings</strong> to configure your preferences and API keys
            </span>
          </li>
        </ul>
      </div>

      {/* Manual Redirect Button */}
      <button
        onClick={() => router.push('/war-room')}
        className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors"
      >
        Go to Command Center
      </button>
    </div>
  );
}
