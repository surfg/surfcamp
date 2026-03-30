import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}

export function getSkillLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced',
  };
  return labels[level] || level;
}

export function getSkillLevelColor(level: string): string {
  const colors: Record<string, string> = {
    beginner: 'bg-emerald-100 text-emerald-700',
    intermediate: 'bg-sky-100 text-sky-700',
    advanced: 'bg-violet-100 text-violet-700',
  };
  return colors[level] || 'bg-gray-100 text-gray-700';
}

export function getWaveTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    beach: 'Beach Break',
    reef: 'Reef Break',
    point: 'Point Break',
  };
  return labels[type] || type;
}

export function getCrowdLabel(level: string): string {
  const labels: Record<string, string> = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    very_high: 'Very High',
  };
  return labels[level] || level;
}
