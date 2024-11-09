# Gallery Storefront Django Project
This Django project's goal is to create a website that serves the dual purpose of a showcase gallery and storefront. 

The storefront uses Shopify as a backend, via shopify-python-api and GraphQL API integration. Both the site and Shopify store use the site as the database of truth, meaning products should only be managed via the Django Project Admin page. 

***This project is not yet complete, and as such, not all capabilities exist.***

### apps.Shopify_App
- [ ] **BUG**: Fix ShopifyAccessToken to retrieve token for user logged in
- [ ] **BUG**: Fix decorators to required Shopify Access Token prior to making GraphQL API calls

**GraphQL API**
- [ ] **BUG**: Fix media upload
  - Desired End State: 
    - Media uploaded via Admin are pushed to Shopify via GraphQL API
  - Current State:
    - api_connector._shop_create_media sends GraphQL request without error and response status "UPLOADED"
    - media fails to upload. Shopify Admin says "media failed processing"
- [ ] FEATURE: Add Online Store Product Link on Product Detail View
- [x] FEATURE: Add support for syncing products with Shopify via GraphQL
- [ ] FEATURE: GraphQL Error Handling
  - [ ] Deserialize JSON response to parse for errors; prevent object from saving to ensure source DB matches Shopify
  - [ ] Notify user of failed sync including error message

### apps.Store
- [ ] Pending

### apps.Main
- [ ] Pending

### apps.Gallery
- [ ] FEATURE: Match source DB model with Shopify Product model
  - [ ] Support Options
  - [ ] Support Variants
  - [ ] Update _shop_sync to perform mutations including options and variants

### General To-Do's
- [ ] Pending