/// <reference types="cypress" />
import '@testing-library/cypress/add-commands';

Cypress.Commands.add('login', (user, pin, virtualKeyboard = false) => {
  cy.findByRole('textbox', { name: /DNI, NIE, Passaporte o usuario/i }).type(user);
  cy.findByLabelText(/Clave de acceso/i).click();

  if (virtualKeyboard) {
    cy.get('[data-testid="VirtualKeyboardNumbersContainer"]').parent().as('vKeyboard');
    pin.split('').forEach(digit => {
      cy.get('@vKeyboard').contains(digit).click();
    });
  } else {
    cy.findByLabelText(/Clave de acceso/i).type(pin);
  }
  cy.findByRole('button', { name: /Acceder/i })
    .should('be.enabled')
    .click();
});

Cypress.on('window:before:load', window => {
  Object.defineProperty(window.navigator, 'language', { value: 'es-ES' });
  Object.defineProperty(window.navigator, 'languages', { value: ['es-ES'] });
});

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, pin) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, pin: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }
