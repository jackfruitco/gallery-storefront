# Gallery Storefront Django Project
This Django project's goal is to create a website that serves the dual purpose of a showcase gallery and storefront. 

The storefront uses Shopify as a backend, via shopify-python-api and GraphQL API integration. Both the site and Shopify store use the site as the database of truth, meaning products should only be managed via the Django Project Admin page. 

***This project is not yet complete, and as such, not all capabilities exist.***

### 1. apps.Shopify_App To-Do's
- [ ] **BUG**: Fix ShopifyAccessToken to retrieve token for user logged in
- [x] ~~**BUG**: Fix decorators to required Shopify Access Token prior to making GraphQL API calls~~ Solved using GraphQL error handling
- [ ] **BUG**: Fix failure to call deleteProduct mutation upon disabling Product.shopify_sync

**GraphQL API**
- [ ] **BUG**: Fix media upload
  - Desired End State: 
    - Media uploaded via Admin are pushed to Shopify via GraphQL API
  - Current State:
    - ShopifyBridge stages media, and creates media. Media fails processing due to 'corrupt file'
- [ ] FEATURE: Add Online Store Product Link on Product Detail View
- [x] FEATURE: Add support for syncing products with Shopify via GraphQL
- [x] FEATURE: GraphQL Error Handling
  - [x] Deserialize JSON response to parse for errors; prevent object from saving to ensure source DB matches Shopify
  - [x] Notify user of failed sync including error message

### 2. apps.Store To-Do's
- [ ] Add order fulfillment processing
- [ ] Add order notifications
- [ ] Add low stock notifications

### 3. apps.Main To-Do's
- [ ] **BUG**: Fix products appearing on site index when Product.display is set to False
- [ ] FEATURE: Add field to Product Model to filter featured images for display on site index

### 4. apps.Gallery To-Do's
- [ ] FEATURE: Match source DB model with Shopify Product model
- [ ] Add gallery support to view variants on single Product detail vew

### 5. Shopify Bridge To-Do's
- [ ] Add full support for Options and Varints
  - [ ] Add models: ProductOption, ProductOptionValue, ProductVariant
  - [ ] Update productSet mutation to support dynamically building productSetInput
- [ ] Add Async support to push Shopify Admin updates to local DB (or local to poll Shopify, if unable to push)

### 6. General To-Do's
- [x] **BUG**: Fix alignment on Admin Login button