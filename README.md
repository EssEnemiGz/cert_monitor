# cert_monitor

This project monitors certificate transparency logs for new domains using [certstream](https://github.com/CaliDog/certstream-server) and stores them in a PostgreSQL database.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/EssEnemiGz/cert_monitor.git
   cd cert_monitor
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Set up the environment variables:**

   Create a `.env` file in the root of the project by copying the `.env.example` file:

   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your database credentials.

2. **Start the database:**

   Run the following command to start the PostgreSQL database in a Docker container:

   ```bash
   docker-compose build && docker-compose up -d
   ```

3. **Run the worker:**

   Execute the following command to start the worker and begin monitoring for new domains:

   ```bash
   python worker.py
   ```

## Database

The project uses a PostgreSQL database to store the domains. The database is automatically initialized with a `domains` table when the Docker container is first started. The schema is defined in the `init.sql` file.

The `domains` table has the following columns:

- `id`: A unique identifier for each record.
- `domain`: The domain name.
- `creation_date`: The timestamp when the domain was added to the database.

## Environment Variables

The following environment variables are required to run the project. They should be defined in the `.env` file:

- `POSTGRES_DB`: The name of the database.
- `POSTGRES_USER`: The username for the database.
- `POSTGRES_PASSWORD`: The password for the database.
- `POSTGRES_HOST`: The host of the database.
- `POSTGRES_PORT`: The port of the database.
- SMTP_SERVER_URL: The SMTP URL you will use (smtp.gmail.com, for example).
- SMTP_SERVER_PORT: The SMTP access port.
- SMTP_USER: The SMTP admin user.
- SMTP_PASSW: The SMTP Password for user.
- SMTP_ALIAS: The email you will use to send the alerts, must be the same email you used to log in if you don't have alias in your server.
- SMTP_ADMIN_EMAIL: The email you will use to receive the alerts.
