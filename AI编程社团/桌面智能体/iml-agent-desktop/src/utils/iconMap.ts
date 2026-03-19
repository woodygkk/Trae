
import {
  Plane,
  FileText,
  Presentation,
  BarChart3,
  Box,
  Plus,
  Github,
  Database,
  MessageSquare,
  Settings,
  LayoutGrid
} from 'lucide-react';

export const IconMap: Record<string, any> = {
  'plane': Plane,
  'file-text': FileText,
  'presentation': Presentation,
  'bar-chart-3': BarChart3,
  'box': Box,
  'plus': Plus,
  'github': Github,
  'database': Database,
  'message-square': MessageSquare,
  'settings': Settings,
  'layout-grid': LayoutGrid,
  'default': Box
};

export const getIconComponent = (iconName: string) => {
  return IconMap[iconName] || IconMap['default'];
};
