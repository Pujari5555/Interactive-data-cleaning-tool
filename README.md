# Interactive Data Cleaning Tool

An interactive, web-based data cleaning tool built with **Django**, designed to simplify and automate essential preprocessing tasks for raw datasets. Users can upload CSV files, preview, clean, and download the cleaned datasets through a step-by-step intuitive dashboard.



## 🚀 Features

- Upload and preview CSV files
- Handle missing values (drop or fill)
- Remove duplicate rows
- Validate and correct data types
- Detect and handle outliers
- Download cleaned datasets in CSV format
- Responsive UI with a collapsible sidebar and smooth animations
- Authentication and session management


## 🛠️ Technologies Used

### 🔧 Frontend
- **HTML, CSS, Bootstrap 5**
- **JavaScript** for interactivity
- **Font Awesome** for icons

### ⚙️ Backend
- **Python & Django** for server-side logic
- **Pandas** for data cleaning operations
- **SQLite** as the database

### 🗃️ Other Tools
- **Git & GitHub** for version control
- Optional deployment on **PythonAnywhere**


## 📐 System Architecture

- **Frontend**: Provides a responsive interface for uploading files and navigating through cleaning steps.
- **Views (Controller)**: Django views manage routing, file handling, and page rendering.
- **Data Cleaning Module**: Implements logic using pandas for cleaning, validation, and transformation.
- **Database**: Uses SQLite to store user sessions and logs.
- **Security**: Django's built-in authentication handles login/logout functionality.


Deployment link: https://datacleaning.pythonanywhere.com/
