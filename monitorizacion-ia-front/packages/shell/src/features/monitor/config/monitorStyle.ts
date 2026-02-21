export type MonitorStyleConfig = {
  theme: {
    pageBackground: string;
    surfaceBackground: string;
    surfaceBorder: string;
    accent: string;
    text: string;
  };
  cards: {
    columns: number;
    showSubtitle: boolean;
    titleAliases: Record<string, string>;
  };
};

export const defaultMonitorStyle: MonitorStyleConfig = {
  theme: {
    pageBackground: '#f4f7fb',
    surfaceBackground: '#ffffff',
    surfaceBorder: '#d9e2ec',
    accent: '#0b5fff',
    text: '#102a43',
  },
  cards: {
    columns: 4,
    showSubtitle: true,
    titleAliases: {},
  },
};
