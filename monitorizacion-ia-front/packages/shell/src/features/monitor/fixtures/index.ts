import { CardsResponse, DashboardDetailResponse, DashboardResponse } from '#/shell/shared/contracts/monitor.contracts';
import { isAllowedUseCase } from '#/shell/shared/config/useCases';

type FixtureBundle = {
  cards: CardsResponse;
  dashboard: DashboardResponse;
  dashboardDetail: DashboardDetailResponse;
};

const fixtureByUseCase: Record<string, FixtureBundle> = {
  hipotecas: {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    cards: require('./hipotecas/cards.json'),
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    dashboard: require('./hipotecas/dashboard.json'),
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    dashboardDetail: require('./hipotecas/dashboard_detail.json'),
  },
  prestamos: {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    cards: require('./prestamos/cards.json'),
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    dashboard: require('./prestamos/dashboard.json'),
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    dashboardDetail: require('./prestamos/dashboard_detail.json'),
  },
};

export const getFixtureByUseCase = (casoDeUso: string): FixtureBundle => {
  if (!isAllowedUseCase(casoDeUso)) {
    return fixtureByUseCase.hipotecas;
  }

  return fixtureByUseCase[casoDeUso] ?? fixtureByUseCase.hipotecas;
};
