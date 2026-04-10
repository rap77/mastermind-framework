'use client';

import { usePathname } from 'next/navigation';
import { Link } from 'next/link';
import {
  LayoutDashboard,
  Brain,
  Lightbulb,
  Settings,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'War Room', href: '/war-room', icon: LayoutDashboard },
  { label: 'Nexus', href: '/nexus', icon: Brain },
  { label: 'Strategy', href: '/strategy', icon: Lightbulb },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 h-16 bg-background border-t md:hidden z-40"
      role="navigation"
      aria-label="Mobile navigation"
    >
      <div className="grid grid-cols-4 h-full">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex flex-col items-center justify-center gap-1 transition-colors',
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )}
              aria-label={item.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
