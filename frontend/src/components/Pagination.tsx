import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalCount: number;
  pageSize: number;
}

export function Pagination({ currentPage, totalPages, onPageChange, totalCount, pageSize }: PaginationProps) {
  const { t } = useLanguage();

  if (totalPages <= 1) return null;

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalCount);

  // Generate page numbers to show
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const showPages = 5; // Max pages to show

    if (totalPages <= showPages + 2) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      if (currentPage > 3) {
        pages.push('...');
      }

      // Show pages around current
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push('...');
      }

      // Always show last page
      pages.push(totalPages);
    }

    return pages;
  };

  const buttonStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '40px',
    height: '40px',
    borderRadius: '10px',
    border: '1px solid #e2e8f0',
    backgroundColor: 'white',
    fontSize: '14px',
    fontWeight: 500,
    color: '#0f172a',
    cursor: 'pointer',
    transition: 'all 0.15s',
  };

  const activeButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#0f172a',
    color: 'white',
    border: '1px solid #0f172a',
  };

  const disabledButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#f8fafc',
    color: '#94a3b8',
    cursor: 'not-allowed',
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '16px',
      marginTop: '40px',
      paddingTop: '24px',
      borderTop: '1px solid #e2e8f0'
    }}>
      {/* Results info */}
      <p style={{
        fontSize: '14px',
        color: '#64748b',
        margin: 0
      }}>
        {t('pagination.showing')} {startItem}-{endItem} {t('pagination.of')} {totalCount}
      </p>

      {/* Page buttons */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        {/* Previous */}
        <button
          onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          style={currentPage === 1 ? disabledButtonStyle : buttonStyle}
        >
          <ChevronLeft style={{ width: '18px', height: '18px' }} />
        </button>

        {/* Page numbers */}
        {getPageNumbers().map((page, index) => (
          page === '...' ? (
            <span
              key={`ellipsis-${index}`}
              style={{
                width: '40px',
                textAlign: 'center',
                color: '#94a3b8',
                fontSize: '14px'
              }}
            >
              ...
            </span>
          ) : (
            <button
              key={page}
              onClick={() => onPageChange(page as number)}
              style={currentPage === page ? activeButtonStyle : buttonStyle}
            >
              {page}
            </button>
          )
        ))}

        {/* Next */}
        <button
          onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          style={currentPage === totalPages ? disabledButtonStyle : buttonStyle}
        >
          <ChevronRight style={{ width: '18px', height: '18px' }} />
        </button>
      </div>
    </div>
  );
}
