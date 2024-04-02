# Trade and Material Assets (TMA) Warehouse

This Python application is designed to automate the management of orders and goods in a warehouse. There are three roles, employee, coordinator, and admin. The employee can create orders, the coordinator can accept or decline the order and replenish the items in stock, and the admin gives permissions and manage the system. 

## Features

 **User Roles:**

- Employee: Can create orders.
- Coordinator: Can accept or decline orders and manage stock replenishment.
- Admin: Manages user permissions and overall system administration.

 **Order Management:**
- Creation of new orders by employees, with the possibility to have multiple items requested in one order
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
### Set up the Python virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

### Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Apply migrations:
Apply Django migrations using

   ```bash
  python manage.py migrate
   ```

### Technologies
- Django
- PostgreSQL


#### License
This app is open-source and distributed under the MIT License.
