import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function NavItem({ icon: Icon, active, onClick }: { icon: any, active?: boolean, onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-10 h-10 rounded-xl flex items-center justify-center transition-all",
        active
          ? "bg-indigo-50 text-indigo-600"
          : "text-gray-400 hover:bg-gray-50 hover:text-gray-600"
      )}>
      <Icon size={20} />
    </button>
  );
}

export function IconButton({ icon: Icon, onClick }: { icon: any, onClick?: () => void }) {
  return (
    <button onClick={onClick} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
      <Icon size={18} />
    </button>
  );
}

export function TabButton({ active, onClick, icon: Icon, label }: { active: boolean, onClick: () => void, icon: any, label: string }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2",
        active
          ? "border-indigo-600 text-indigo-600"
          : "border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50"
      )}
    >
      <Icon size={14} />
      {label}
    </button>
  );
}
