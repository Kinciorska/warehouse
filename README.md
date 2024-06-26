# Trade and Material Assets (TMA) Warehouse

This Python application is designed to automate the management of orders and items in a warehouse. There are three roles, employee, coordinator, and admin. The employee can create orders, the coordinator can accept or decline the order and replenish the items in stock, and the admin gives permissions and manage the system. 

## Features

 **User Roles:**
- Employee: Can create orders.
- Coordinator: Can accept or decline orders and manage stock replenishment.
- Admin: Manages user permissions and overall system administration.

**Item Management:**
- New item creation and stock replenishment made by coordinators.
- Search and filter functionality for easier access.

 **Order Management:**
- Creation of new orders by employees, with the possibility to have multiple items in one order
- Search and filter functionality for easier access.
- Stock management, overview of orders by coordinators.

 **Secure login system for different user roles:**
- Role-based access control to restrict functionalities based on user privileges.
- Ability for admins to define and modify user permissions.


## Getting Started

Follow these steps to build and run the app.

### Clone the repository:

   ```bash
   git clone https://github.com/Kinciorska/warehouse.git
   ```
### Build the Docker Image:

Needed environment files:

- .django

- .postgres

Environment files should be located in .envs directory, examples of these environment files are available in the same directory.
 
Build the Docker container using
```
docker-compose build
```
### Build the Docker Container:
Run the Docker container in the background using
```
docker-compose up -d
```
### Apply migrations:
Apply Django migrations using

   ```bash
  docker-compose run web python manage.py migrate
   ```

### Technologies
- Django
- PostgreSQL
- Docker


#### License
This app is open-source and distributed under the MIT License.
