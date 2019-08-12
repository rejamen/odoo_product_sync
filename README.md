# Odoo 12 Product Synchronisation
> sync products between Odoo 12 and an external system 

Module to synchronise products between Odoo (version 12) and an external system. The idea behind is to do a synchronisation to Amazon, Magento or Ebay. It uses the ​OCA connector module​ as base for the synchronisation and extends it to get the sync process done.

The product synchronisation its done in both ways:
1.	odoo -> external system
	If the product changes in Odoo it is synchronised to the external system.

2.	external system -> odoo
	If the product changes in the external system it is possible to get these changes. 

In product detail view it has been added a widget to check the synchronisation state. If the external product data is different than the Odoo product data it shows “Sync needed”, otherwise it shows “Synced”.

## Installing / Getting started

To test this module we use Docker, which install Odoo12, Postgres 9.5 and Magento 2. 
All you need is Docker installed and to follow next steps:

```shell
git clone https://github.com/rejamen/odoo_product_sync.git
cd odoo_product_sync
docker-compose up
```

You can go now to your browser on https://localhost:8069 to see Odoo database admin panel. Create a new database (set db name, email and password). When database is already created search in Apps section for odoo_product_sync module and install it. All dependencies will be automatically installed.
