'use client';

import { useState } from 'react';
import { CheckCircle2, XCircle, Loader2, ArrowLeft, ArrowRight } from 'lucide-react';
import { useOnboardingStore } from '@/stores/onboardingStore';
import { toastError, toastSuccess } from '@/lib/toast';
import { cn } from '@/lib/utils';

export function ValidationStep() {
  const { adapterConfig, companyData, prevStep, completeOnboarding } = useOnboardingStore();
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const validateAdapter = async () => {
    setIsValidating(true);
    setValidationResult(null);

    try {
      // Simulate API validation (replace with actual validation)
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Mock validation logic
      const isValid =
        (adapterConfig.provider === 'local' && adapterConfig.baseUrl) ||
        (adapterConfig.apiKey && adapterConfig.apiKey.startsWith('sk-'));

      if (isValid) {
        setValidationResult({
          success: true,
          message: `Successfully connected to ${adapterConfig.provider === 'openai' ? 'OpenAI' : adapterConfig.provider === 'anthropic' ? 'Anthropic' : 'Local LLM'}!`,
        });
        toastSuccess('Adapter validated successfully');
      } else {
        setValidationResult({
          success: false,
          message: 'Invalid API key or configuration. Please check your credentials.',
        });
        toastError('Adapter validation failed');
      }
    } catch (error) {
      setValidationResult({
        success: false,
        message: error instanceof Error ? error.message : 'Validation failed',
      });
      toastError('Validation failed');
    } finally {
      setIsValidating(false);
    }
  };

  const handleComplete = () => {
    if (validationResult?.success) {
      completeOnboarding();
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="space-y-4 pb-4 border-b">
        <h2 className="text-xl font-semibold">Review your setup</h2>

        <div className="bg-muted/50 rounded-lg p-4 space-y-2">
          <div>
            <span className="text-sm text-muted-foreground">Company:</span>{' '}
            <span className="font-medium">{companyData.name || 'Not set'}</span>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Industry:</span>{' '}
            <span className="font-medium">{companyData.industry || 'Not set'}</span>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Goal:</span>{' '}
            <span className="font-medium">{companyData.goal || 'Not set'}</span>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Adapter:</span>{' '}
            <span className="font-medium capitalize">{adapterConfig.provider}</span>
          </div>
        </div>
      </div>

      {/* Validation */}
      <div className="space-y-4">
        <h3 className="font-semibold">Test your adapter connection</h3>
        <p className="text-sm text-muted-foreground">
          We'll make a test call to ensure your {adapterConfig.provider} adapter is working correctly.
        </p>

        {!validationResult ? (
          <button
            onClick={validateAdapter}
            disabled={isValidating}
            className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isValidating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Validating...
              </>
            ) : (
              'Test Connection'
            )}
          </button>
        ) : (
          <div
            className={cn(
              'p-4 rounded-lg flex items-start gap-3',
              validationResult.success
                ? 'bg-green-500/10 border border-green-500/20'
                : 'bg-destructive/10 border border-destructive/20'
            )}
          >
            {validationResult.success ? (
              <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <div
                className={cn(
                  'font-semibold',
                  validationResult.success ? 'text-green-500' : 'text-destructive'
                )}
              >
                {validationResult.success ? 'Success!' : 'Validation Failed'}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {validationResult.message}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between pt-4">
        <button
          onClick={prevStep}
          className="px-6 py-2 flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <button
          onClick={handleComplete}
          disabled={!validationResult?.success}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          Complete Setup
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
