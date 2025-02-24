import { cn } from '@/lib/utils';

export function Avatar({ name, className }) {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  return (
    <div
      className={cn(
        'relative inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-medium text-white',
        className
      )}
    >
      <span>{initials}</span>
    </div>
  );
}