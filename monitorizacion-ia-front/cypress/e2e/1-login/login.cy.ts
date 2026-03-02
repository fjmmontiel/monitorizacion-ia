describe('Monitorización end-to-end journeys', () => {
  it('recorre Home -> Monitor -> Admin con configuración dinámica de vistas', () => {
    cy.intercept('GET', '**/datops/overview', {
      statusCode: 200,
      body: {
        schema_version: 'v1',
        generated_at: new Date().toISOString(),
        profile: 'e2e',
        use_cases: [{ id: 'hipotecas', adapter: 'native', timeout_ms: 2000, routes: { cards: '/cards?caso_de_uso=hipotecas', dashboard: '/dashboard?caso_de_uso=hipotecas', dashboard_detail: '/dashboard_detail?caso_de_uso=hipotecas&id={id}' } }],
      },
    }).as('datopsOverview');

    cy.intercept('GET', '**/admin/view-configs', {
      statusCode: 200,
      body: [
        {
          id: 'vista-ops',
          name: 'Vista Operativa',
          system: 'hipotecas',
          enabled: true,
          components: [
            { id: 'cards-main', type: 'cards', title: 'Resumen', data_source: '/cards', position: 0 },
            { id: 'table-main', type: 'table', title: 'Tabla', data_source: '/dashboard', position: 1 },
            { id: 'txt', type: 'text', title: 'Notas', data_source: '/none', position: 2, config: { text: 'Texto dinámico' } },
          ],
        },
      ],
    }).as('getViews');

    cy.intercept('POST', '**/cards?caso_de_uso=*', { statusCode: 200, body: { cards: [{ title: 'Gestiones', value: 10 }] } }).as('cards');
    cy.intercept('POST', '**/dashboard?caso_de_uso=*', { statusCode: 200, body: { table: { columns: [{ key: 'gestor', label: 'Gestor' }], rows: [{ id: 'case-1', detail: { action: 'Ver detalle' }, gestor: 'Ana' }] } } }).as('dashboard');
    cy.intercept('POST', '**/dashboard_detail?caso_de_uso=*&id=*', { statusCode: 200, body: { left: { messages: [{ role: 'assistant', text: 'Caso mock' }] }, right: [{ type: 'list', title: 'Evidencias', items: ['item 1'] }] } }).as('detail');
    cy.intercept('POST', '**/admin/view-configs', { statusCode: 200, body: { id: 'vista-hipotecas', name: 'Vista Hipotecas', system: 'hipotecas', enabled: true, components: [{ id: 'cards-main', type: 'cards', title: 'KPIs', data_source: '/cards', position: 0 }] } }).as('createView');

    cy.visit('/home');
    cy.wait('@datopsOverview');
    cy.contains('Home de monitorización').should('be.visible');

    cy.contains('Abrir monitor').click();
    cy.wait('@getViews');
    cy.wait('@cards');
    cy.wait('@dashboard');
    cy.contains('Vistas').should('be.visible');
    cy.contains('Vista Operativa').should('be.visible');
    cy.contains('Texto dinámico').should('be.visible');

    cy.contains('Ver detalle').click();
    cy.wait('@detail');
    cy.contains('Caso mock').should('be.visible');

    cy.visit('/admin');
    cy.wait('@getViews');
    cy.get('input[placeholder="id de vista"]').clear().type('vista-hipotecas');
    cy.get('input[placeholder="nombre visible"]').clear().type('Vista Hipotecas');
    cy.get('input[placeholder="sistema"]').clear().type('hipotecas');
    cy.get('input[placeholder="id componente"]').type('cards-main');
    cy.get('input[placeholder="título"]').type('KPIs');
    cy.get('input[placeholder="data source"]').clear().type('/cards');
    cy.get('textarea[placeholder*="config JSON por componente"]').clear().type('{"text":"Widget reutilizable"}');
    cy.contains('Añadir componente').click();
    cy.contains('Crear vista').click();
    cy.wait('@createView');
  });
});

export {};
