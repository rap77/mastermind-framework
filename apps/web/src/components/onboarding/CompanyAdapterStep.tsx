'use client';

import { useState } from 'react';
import { Building2, Cpu, ArrowLeft, ArrowRight } from 'lucide-react';
import { useOnboardingStore } from '@/stores/onboardingStore';
import { cn } from '@/lib/utils';

const INDUSTRIES = [
  'Technology',
  'Finance',
  'Healthcare',
  'E-commerce',
  'SaaS',
  'Manufacturing',
  'Other',
];

const GOALS = [
  'Product Strategy',
  'UX Research',
  'UI Design',
  'Frontend Development',
  'Backend Development',
  'QA & Testing',
  'Growth & Analytics',
];

const ADAPTERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4, GPT-4 Turbo',
    icon: '🤖',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Claude 3 Opus, Sonnet',
    icon: '🧠',
  },
  {
    id: 'local',
    name: 'Local LLM',
    description: 'Ollama, LocalAI',
    icon: '💻',
  },
];

export function CompanyAdapterStep() {
  const { companyData, adapterConfig, setCompanyData, setAdapterConfig, prevStep, nextStep } =
    useOnboardingStore();

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!companyData.name.trim()) {
      newErrors.name = 'Company name is required';
    }

    if (!companyData.industry) {
      newErrors.industry = 'Please select an industry';
    }

    if (!companyData.goal) {
      newErrors.goal = 'Please select a primary goal';
    }

    if (adapterConfig.provider === 'local' && !adapterConfig.baseUrl) {
      newErrors.baseUrl = 'Base URL is required for local LLM';
    }

    if (adapterConfig.provider !== 'local' && !adapterConfig.apiKey) {
      newErrors.apiKey = 'API key is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validate()) {
      nextStep();
    }
  };

  return (
    <div className="space-y-6">
      {/* Company Info Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b">
          <Building2 className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-semibold">Tell us about your company</h2>
        </div>

        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Company Name <span className="text-destructive">*</span>
          </label>
          <input
            type="text"
            value={companyData.name}
            onChange={(e) => setCompanyData({ name: e.target.value })}
            placeholder="Acme Inc."
            className={cn(
              'w-full px-4 py-2 rounded-lg border bg-background',
              errors.name && 'border-destructive'
            )}
          />
          {errors.name && <p className="text-destructive text-sm mt-1">{errors.name}</p>}
        </div>

        {/* Industry */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Industry <span className="text-destructive">*</span>
          </label>
          <select
            value={companyData.industry}
            onChange={(e) => setCompanyData({ industry: e.target.value })}
            className={cn(
              'w-full px-4 py-2 rounded-lg border bg-background',
              errors.industry && 'border-destructive'
            )}
          >
            <option value="">Select industry</option>
            {INDUSTRIES.map((industry) => (
              <option key={industry} value={industry}>
                {industry}
              </option>
            ))}
          </select>
          {errors.industry && <p className="text-destructive text-sm mt-1">{errors.industry}</p>}
        </div>

        {/* Primary Goal */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Primary Goal <span className="text-destructive">*</span>
          </label>
          <select
            value={companyData.goal}
            onChange={(e) => setCompanyData({ goal: e.target.value })}
            className={cn(
              'w-full px-4 py-2 rounded-lg border bg-background',
              errors.goal && 'border-destructive'
            )}
          >
            <option value="">Select primary goal</option>
            {GOALS.map((goal) => (
              <option key={goal} value={goal}>
                {goal}
              </option>
            ))}
          </select>
          {errors.goal && <p className="text-destructive text-sm mt-1">{errors.goal}</p>}
        </div>
      </div>

      {/* Adapter Section */}
      <div className="space-y-4 pt-4 border-t">
        <div className="flex items-center gap-3 pb-4 border-b">
          <Cpu className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-semibold">Choose your AI adapter</h2>
        </div>

        {/* Adapter Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {ADAPTERS.map((adapter) => (
            <button
              key={adapter.id}
              onClick={() => setAdapterConfig({ provider: adapter.id as any })}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                adapterConfig.provider === adapter.id
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              )}
            >
              <div className="text-2xl mb-2">{adapter.icon}</div>
              <div className="font-semibold">{adapter.name}</div>
              <div className="text-sm text-muted-foreground">{adapter.description}</div>
            </button>
          ))}
        </div>

        {/* API Key / Base URL */}
        {adapterConfig.provider === 'local' ? (
          <div>
            <label className="block text-sm font-medium mb-2">
              Base URL <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={adapterConfig.baseUrl}
              onChange={(e) => setAdapterConfig({ baseUrl: e.target.value })}
              placeholder="http://localhost:11434"
              className={cn(
                'w-full px-4 py-2 rounded-lg border bg-background',
                errors.baseUrl && 'border-destructive'
              )}
            />
            {errors.baseUrl && <p className="text-destructive text-sm mt-1">{errors.baseUrl}</p>}
            <p className="text-sm text-muted-foreground mt-1">
              Your local LLM endpoint (e.g., Ollama, LocalAI)
            </p>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium mb-2">
              API Key <span className="text-destructive">*</span>
            </label>
            <input
              type="password"
              value={adapterConfig.apiKey}
              onChange={(e) => setAdapterConfig({ apiKey: e.target.value })}
              placeholder="sk-..."
              className={cn(
                'w-full px-4 py-2 rounded-lg border bg-background',
                errors.apiKey && 'border-destructive'
              )}
            />
            {errors.apiKey && <p className="text-destructive text-sm mt-1">{errors.apiKey}</p>}
            <p className="text-sm text-muted-foreground mt-1">
              Your {adapterConfig.provider === 'openai' ? 'OpenAI' : 'Anthropic'} API key
            </p>
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
          onClick={handleNext}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors flex items-center gap-2"
        >
          Next
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
