import { Command } from '@/stores/commandStore';

// Router navigation helper (initialized when command palette mounts)
let navigate: (path: string) => void = (path: string) => {
  if (typeof window !== 'undefined') {
    window.location.href = path;
  }
};

export const COMMANDS: Command[] = [
  // ==================== NAVIGATION ====================
  {
    id: 'nav-war-room',
    label: 'Command Center',
    category: 'Navigation',
    icon: 'Navigation',
    action: () => navigate('/war-room'),
    keywords: ['dashboard', 'home', 'main'],
  },
  {
    id: 'nav-nexus',
    label: 'The Nexus',
    category: 'Navigation',
    icon: 'Navigation',
    action: () => navigate('/nexus'),
    keywords: ['nexus', 'hub', 'central'],
  },
  {
    id: 'nav-strategy',
    label: 'Strategy Vault',
    category: 'Navigation',
    icon: 'Navigation',
    action: () => navigate('/strategy'),
    keywords: ['strategy', 'vault', 'plans'],
  },
  {
    id: 'nav-engine',
    label: 'Engine Room',
    category: 'Navigation',
    icon: 'Navigation',
    action: () => navigate('/engine'),
    keywords: ['engine', 'room', 'backend'],
  },

  // ==================== BRAINS (grouped by domain per Brain #7 Condition 3) ====================
  // Product Strategy (4 brains)
  {
    id: 'brain-product-vision',
    label: 'Product Vision',
    category: 'Brains',
    subcategory: 'Product Strategy',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/product-vision/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['product', 'vision', 'strategy'],
  },
  {
    id: 'brain-market-fit',
    label: 'Market Fit',
    category: 'Brains',
    subcategory: 'Product Strategy',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/market-fit/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['market', 'fit', 'pmf'],
  },
  {
    id: 'brain-roadmap',
    label: 'Roadmap Planner',
    category: 'Brains',
    subcategory: 'Product Strategy',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/roadmap/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['roadmap', 'planning', 'timeline'],
  },
  {
    id: 'brain-prioritization',
    label: 'Prioritization',
    category: 'Brains',
    subcategory: 'Product Strategy',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/prioritization/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['priority', 'rank', 'important'],
  },

  // UX Research (4 brains)
  {
    id: 'brain-user-research',
    label: 'User Research',
    category: 'Brains',
    subcategory: 'UX Research',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/user-research/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['user', 'research', 'interviews'],
  },
  {
    id: 'brain-personas',
    label: 'Personas',
    category: 'Brains',
    subcategory: 'UX Research',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/personas/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['persona', 'profile', 'user type'],
  },
  {
    id: 'brain-journey-map',
    label: 'Journey Map',
    category: 'Brains',
    subcategory: 'UX Research',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/journey-map/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['journey', 'map', 'flow'],
  },
  {
    id: 'brain-usability',
    label: 'Usability Testing',
    category: 'Brains',
    subcategory: 'UX Research',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/usability/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['usability', 'testing', 'ux'],
  },

  // UI Design (4 brains)
  {
    id: 'brain-design-system',
    label: 'Design System',
    category: 'Brains',
    subcategory: 'UI Design',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/design-system/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['design', 'system', 'components'],
  },
  {
    id: 'brain-visual-design',
    label: 'Visual Design',
    category: 'Brains',
    subcategory: 'UI Design',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/visual-design/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['visual', 'design', 'aesthetic'],
  },
  {
    id: 'brain-prototyping',
    label: 'Prototyping',
    category: 'Brains',
    subcategory: 'UI Design',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/prototyping/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['prototype', 'mockup', 'wireframe'],
  },
  {
    id: 'brain-accessibility',
    label: 'Accessibility',
    category: 'Brains',
    subcategory: 'UI Design',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/accessibility/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['a11y', 'accessibility', 'wcag'],
  },

  // Frontend (4 brains)
  {
    id: 'brain-architecture',
    label: 'Frontend Architecture',
    category: 'Brains',
    subcategory: 'Frontend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/frontend-architecture/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['frontend', 'architecture', 'structure'],
  },
  {
    id: 'brain-state-management',
    label: 'State Management',
    category: 'Brains',
    subcategory: 'Frontend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/state-management/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['state', 'management', 'store'],
  },
  {
    id: 'brain-performance',
    label: 'Performance',
    category: 'Brains',
    subcategory: 'Frontend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/performance/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['performance', 'optimization', 'speed'],
  },
  {
    id: 'brain-testing',
    label: 'Frontend Testing',
    category: 'Brains',
    subcategory: 'Frontend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/frontend-testing/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['testing', 'frontend', 'unit', 'e2e'],
  },

  // Backend (4 brains)
  {
    id: 'brain-api-design',
    label: 'API Design',
    category: 'Brains',
    subcategory: 'Backend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/api-design/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['api', 'rest', 'graphql'],
  },
  {
    id: 'brain-database',
    label: 'Database Design',
    category: 'Brains',
    subcategory: 'Backend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/database/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['database', 'sql', 'schema'],
  },
  {
    id: 'brain-auth',
    label: 'Authentication',
    category: 'Brains',
    subcategory: 'Backend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/auth/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['auth', 'authentication', 'security'],
  },
  {
    id: 'brain-scalability',
    label: 'Scalability',
    category: 'Brains',
    subcategory: 'Backend',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/scalability/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['scale', 'scalability', 'load'],
  },

  // QA/DevOps (4 brains)
  {
    id: 'brain-qa-strategy',
    label: 'QA Strategy',
    category: 'Brains',
    subcategory: 'QA/DevOps',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/qa-strategy/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['qa', 'quality', 'assurance'],
  },
  {
    id: 'brain-ci-cd',
    label: 'CI/CD',
    category: 'Brains',
    subcategory: 'QA/DevOps',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/ci-cd/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['ci', 'cd', 'deployment'],
  },
  {
    id: 'brain-monitoring',
    label: 'Monitoring',
    category: 'Brains',
    subcategory: 'QA/DevOps',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/monitoring/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['monitor', 'logging', 'observability'],
  },
  {
    id: 'brain-incidents',
    label: 'Incident Response',
    category: 'Brains',
    subcategory: 'QA/DevOps',
    icon: 'Brains',
    action: async () => {
      const res = await fetch('/api/brains/incidents/trigger', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to trigger brain');
    },
    keywords: ['incident', 'response', 'debugging'],
  },

  // ==================== ACTIONS ====================
  {
    id: 'action-create-company',
    label: 'Create Company',
    category: 'Actions',
    icon: 'Actions',
    action: () => navigate('/companies/new'),
    keywords: ['create', 'company', 'new', 'add'],
  },
  {
    id: 'action-switch-company',
    label: 'Switch Company',
    category: 'Actions',
    icon: 'Actions',
    action: () => navigate('/companies'),
    keywords: ['switch', 'company', 'change'],
  },
  {
    id: 'action-export',
    label: 'Export Data',
    category: 'Actions',
    icon: 'Actions',
    action: () => navigate('/settings/export'),
    keywords: ['export', 'download', 'data'],
  },

  // ==================== SETTINGS ====================
  {
    id: 'settings-api-keys',
    label: 'API Keys',
    category: 'Settings',
    icon: 'Settings',
    action: () => navigate('/settings/api-keys'),
    keywords: ['api', 'keys', 'tokens'],
  },
  {
    id: 'settings-brain-config',
    label: 'Brain Configuration',
    category: 'Settings',
    icon: 'Settings',
    action: () => navigate('/settings/brains'),
    keywords: ['brain', 'config', 'settings'],
  },
  {
    id: 'settings-profile',
    label: 'User Profile',
    category: 'Settings',
    icon: 'Settings',
    action: () => navigate('/settings/profile'),
    keywords: ['profile', 'user', 'account'],
  },
];

// Initialize router navigation helper
export function initCommandRouter(router: { push: (path: string) => void }) {
  navigate = (path: string) => router.push(path);
}
