# NewsWebSite

A Flask-based web application that fetches and displays ranked articles from various sources. The application includes an admin interface for managing configurations and RSS sources.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Admin Interface](#admin-interface)
- [API Endpoints](#api-endpoints)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Features

- Display ranked articles on the homepage.
- Admin interface for managing application configurations and RSS sources.
- Basic authentication for admin routes.
- RESTful API to fetch articles.

## Technologies Used

- Python
- Flask
- SQLite
- Jinja2 (for templating)
- dotenv (for environment variable management)
- Logging

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/NewsWebSite.git
   cd NewsWebSite
   ```

2. Create a virtual environment:
   ```bash
   python -m venv test_env
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source test_env/bin/activate
     ```
   - On Windows:
     ```bash
     test_env\Scripts\activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```plaintext
   FLASK_SECRET_KEY=your_secret_key
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   DB_NAME=your_database_name.db
   ```

## Usage

To run the application, use the following command:

bash
python -m frontend.app

Visit `http://127.0.0.1:5000` in your web browser to access the application.

## Configuration

The application configuration can be managed through the admin interface. You can update settings such as RSS feed sources and other application parameters.

## Admin Interface

Access the admin interface at `http://127.0.0.1:5000/admin`. You will need to log in using the credentials specified in your `.env` file.

## API Endpoints

- **GET /api/articles**: Fetches ranked articles in JSON format.

## Logging

The application uses logging to track events and errors. Logs are printed to the console and can be configured to be saved to a file.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any changes or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
