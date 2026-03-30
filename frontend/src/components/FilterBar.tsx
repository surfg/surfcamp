import { useState } from 'react';
import { SlidersHorizontal, X, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { FilterParams } from '../types';
import { cn } from '../lib/utils';

interface FilterBarProps {
  filters: FilterParams;
  onFilterChange: (filters: FilterParams) => void;
}

const SKILL_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

const PRICE_RANGES = [
  { min: 0, max: 50, label: 'Under $50' },
  { min: 50, max: 100, label: '$50 - $100' },
  { min: 100, max: 200, label: '$100 - $200' },
  { min: 200, max: undefined, label: '$200+' },
];

export function FilterBar({ filters, onFilterChange }: FilterBarProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const activeFiltersCount = Object.values(filters).filter(
    (v) => v !== undefined && v !== ''
  ).length;

  const handleSkillLevelChange = (level: string) => {
    onFilterChange({
      ...filters,
      skill_level: filters.skill_level === level ? undefined : level,
    });
  };

  const handlePriceChange = (min?: number, max?: number) => {
    const isActive = filters.min_price === min && filters.max_price === max;
    onFilterChange({
      ...filters,
      min_price: isActive ? undefined : min,
      max_price: isActive ? undefined : max,
    });
  };

  const handleToggle = (key: keyof FilterParams) => {
    onFilterChange({
      ...filters,
      [key]: filters[key] ? undefined : true,
    });
  };

  const clearFilters = () => {
    onFilterChange({});
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-gray-700 font-medium hover:text-sky-600 transition-colors"
        >
          <SlidersHorizontal className="w-5 h-5" />
          <span>Filters</span>
          {activeFiltersCount > 0 && (
            <span className="px-2 py-0.5 bg-sky-100 text-sky-700 text-xs font-semibold rounded-full">
              {activeFiltersCount}
            </span>
          )}
          <ChevronDown
            className={cn(
              'w-4 h-4 transition-transform',
              isExpanded && 'rotate-180'
            )}
          />
        </button>

        {activeFiltersCount > 0 && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-500 transition-colors"
          >
            <X className="w-4 h-4" />
            Clear all
          </button>
        )}
      </div>

      {/* Expanded filters */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-6">
              {/* Skill Level */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Skill Level
                </h4>
                <div className="flex flex-wrap gap-2">
                  {SKILL_LEVELS.map((level) => (
                    <button
                      key={level.value}
                      onClick={() => handleSkillLevelChange(level.value)}
                      className={cn(
                        'px-4 py-2 rounded-full text-sm font-medium transition-all',
                        filters.skill_level === level.value
                          ? 'bg-sky-500 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      )}
                    >
                      {level.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Price Range */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Price per night
                </h4>
                <div className="flex flex-wrap gap-2">
                  {PRICE_RANGES.map((range) => {
                    const isActive =
                      filters.min_price === range.min &&
                      filters.max_price === range.max;
                    return (
                      <button
                        key={range.label}
                        onClick={() => handlePriceChange(range.min, range.max)}
                        className={cn(
                          'px-4 py-2 rounded-full text-sm font-medium transition-all',
                          isActive
                            ? 'bg-sky-500 text-white shadow-md'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        )}
                      >
                        {range.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Amenities */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Amenities
                </h4>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => handleToggle('has_pool')}
                    className={cn(
                      'px-4 py-2 rounded-full text-sm font-medium transition-all',
                      filters.has_pool
                        ? 'bg-sky-500 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    )}
                  >
                    Pool
                  </button>
                  <button
                    onClick={() => handleToggle('has_yoga')}
                    className={cn(
                      'px-4 py-2 rounded-full text-sm font-medium transition-all',
                      filters.has_yoga
                        ? 'bg-sky-500 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    )}
                  >
                    Yoga
                  </button>
                  <button
                    onClick={() => handleToggle('has_bed_breakfast')}
                    className={cn(
                      'px-4 py-2 rounded-full text-sm font-medium transition-all',
                      filters.has_bed_breakfast
                        ? 'bg-sky-500 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    )}
                  >
                    B&B Available
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
