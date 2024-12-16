describe('Property Listing Page', () => {
  beforeEach(() => {
    // Visit the property listing page
    cy.visit('/properties');
    
    // Mock the API response for properties
    cy.intercept('GET', '/api/properties', {
      statusCode: 200,
      body: [
        {
          id: '1',
          title: 'Test Property',
          address: '123 Test St',
          price: 1000,
          status: 'available',
        },
      ],
    }).as('getProperties');
  });

  it('displays property listings', () => {
    // Wait for the API response
    cy.wait('@getProperties');

    // Check if properties are displayed
    cy.get('[data-testid="property-card"]').should('have.length.at.least', 1);
    cy.contains('Test Property').should('be.visible');
    cy.contains('123 Test St').should('be.visible');
    cy.contains('$1,000').should('be.visible');
  });

  it('filters properties correctly', () => {
    cy.wait('@getProperties');

    // Use the filter
    cy.get('[data-testid="status-filter"]').click();
    cy.contains('Available').click();

    // Verify filtered results
    cy.get('[data-testid="property-card"]')
      .should('have.length.at.least', 1)
      .and('contain', 'available');
  });

  it('handles search functionality', () => {
    cy.wait('@getProperties');

    // Type in search box
    cy.get('[data-testid="search-input"]').type('Test Property');

    // Verify search results
    cy.get('[data-testid="property-card"]')
      .should('have.length', 1)
      .and('contain', 'Test Property');
  });

  it('navigates to property details', () => {
    cy.wait('@getProperties');

    // Click on a property card
    cy.get('[data-testid="property-card"]').first().click();

    // Verify navigation to detail page
    cy.url().should('include', '/properties/1');
    cy.contains('Test Property').should('be.visible');
  });
});
