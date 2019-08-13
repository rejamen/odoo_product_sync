# Odoo 12 Product Synchronisation
> sync products between Odoo 12 and an external system 

Module to synchronise products between Odoo (version 12) and an external system. The idea behind is to do a synchronisation to Amazon, Magento or Ebay. It uses the ​OCA connector module​ as base for the synchronisation and extends it to get the sync process done.

The product synchronisation its done in both ways:
1.	odoo -> external system
	If the product changes in Odoo it is synchronised to the external system.

2.	external system -> odoo
	If the product changes in the external system it is possible to get these changes. 

In product detail view it has been added a button (after Archive button) to check the synchronisation state. If the external product data is different than the Odoo product data it shows “Sync", otherwise it hides.

## Installing / Getting started

To test this module we use Docker, which install Odoo12 and Postgres 9.5.
All you need is Docker installed and to follow next steps:

```shell
git clone https://github.com/rejamen/odoo_product_sync.git
cd odoo_product_sync
docker-compose up
```
You can go now to your browser on https://localhost:8069 to see Odoo database admin panel. Create a new database (set database name, email and password). 

When database is already created search in Apps section and install following apps:
1. Stock
2. odoo_product_sync

If you have this error: Unable to install module "component" because an external dependency is not met: No module named cachetools; you can solve with following commands and containers running:

```shell
docker exec -it odoo bash
pip3 install cachetools==2.0.1
```

You need to restart odoo container after that:

```shell
Ctrl + C (Cmd + C in Macos)
docker-compose up
```

When all its done, you can see product list in Inventory->Master data->Products.

## Dockerized Magento

You can test it using a Dockerized Magento version 2.3.1 also included. Just go into docker-magento2 folder and run the containers

```shell
cd docker-magento2
docker-compose up
```

In your browser go to https://localhost and you will see the Magento Admin. Use following credentials and you will have Magento installed.
	Database Server Host: db 
	Database Server Username: magento
	Database Server Password: magento
	Database Name: magento

In https://localhost/admin (user: admin, password: magentorocks1) you can manage your Magento site.





