from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
import logging
import pandas as pd
from django.http import JsonResponse
import csv
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import JsonResponse, HttpResponse
import logging

from django.core.files.storage import FileSystemStorage
import uuid
from django.conf import settings
logging.basicConfig(level=logging.DEBUG)
import sys
import re
from django.shortcuts import render

from io import StringIO



logger = logging.getLogger(__name__)
import os
import pandas as pd
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def home(request):
    return render(request, 'datacleaning/home.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
        else:
            # Create a new user (note: store hashed password in real apps)
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Signup successful! Please login.')
            return redirect('login')

    return render(request, 'datacleaning/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log in the user and redirect to the dashboard
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')  # Redirect to dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'datacleaning/login.html')

def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to login after logging out

@login_required  # Ensure the user is logged in before accessing the profile
def profile_view(request):
    return render(request, 'datacleaning/profile.html')

@login_required  # Ensure the user is logged in before accessing the dashboard
def dashboard(request):
    # Retrieve the logged-in user's username
    username = request.user.username  # Using Django's built-in User model
    return render(request, 'datacleaning/dashboard.html', {'username': username})
@login_required
@csrf_exempt
def cleaning_view(request):
    return render(request, 'datacleaning/cleaning.html')

@login_required
@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Save the file to the media folder
        filename = f"{uuid.uuid4().hex}_{file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Read the file into a DataFrame
        try:
            if file.name.endswith(('.csv', '.xlsx', '.txt')):
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file_path, quotechar='"')
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file_path)  # Ensure quoted commas are handled correctly
            else:
                return JsonResponse({'error': 'Invalid file format'}, status=400)

            # Check if the DataFrame is empty
            if df.empty:
                return JsonResponse({'success': False, 'error': 'The file contains no data.'}, status=400)

            # Generate HTML table preview for the first 5 rows
            preview_html = df.head(5).to_html(classes='table table-striped', index=False)
            return JsonResponse({'success': True, 'preview': preview_html})

        except Exception as e:
            return JsonResponse({'error': f"Error reading file: {str(e)}"}, status=400)
    return JsonResponse({'error': 'No file uploaded'}, status=400)



@login_required
@csrf_exempt
def validate_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()

        # Save the file in the media directory
        try:
            file_name = fs.save(file.name, file)
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            logging.info(f"File {file_name} saved successfully.")
        except Exception as e:
            logging.error(f"Error saving file {file.name}: {str(e)}")
            return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=400)

        try:
            # Try reading the CSV with different encodings
            encodings = ['utf-8', 'ISO-8859-1', 'latin1']
            df = None
            for encoding in encodings:
                try:
                    logging.info(f"Trying to read the file with encoding: {encoding}")
                    df = pd.read_csv(file_path, encoding=encoding)
                    logging.info(f"File read successfully with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    logging.error(f"Failed to decode with encoding: {encoding}")
                    continue  # Try next encoding if decoding fails

            if df is None:
                return JsonResponse({'error': 'Unable to decode the file with supported encodings.'}, status=400)

            # Basic Structure Validation
            if df.empty:
                return JsonResponse({'error': 'The dataset is empty.'}, status=400)

            # Dynamic Column Validation
            missing_columns = [col for col in df.columns if df[col].notnull().sum() == 0]  # At least one non-null value required

            if missing_columns:
                return JsonResponse({'error': f'These columns contain only missing values: {", ".join(missing_columns)}'}, status=400)

            # Data Type Validation - Check if data types seem inconsistent
            invalid_data = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    non_numeric_data = df[~df[col].apply(lambda x: pd.api.types.is_numeric_dtype(type(x)))]
                elif df[col].dtype in ['float64', 'int64']:
                    if df[col].isnull().any():
                        invalid_data.append(f"Missing values found in numeric column '{col}'")

            missing_values = df.isnull().sum().to_dict()
            missing_value_columns = {col: count for col, count in missing_values.items() if count > 0}

            # Prepare the validation data
            data_info = {
                'columns': list(df.columns),
                'shape': df.shape,
                'missing_value_columns': missing_value_columns,
                'invalid_data': invalid_data,
            }

            # Store the DataFrame in session for future use (optional, can be removed for performance)
            request.session['df'] = df.to_dict()

            # Return the validation data
            return JsonResponse(data_info)

        except Exception as e:
            logging.error(f"Error processing the file: {str(e)}")
            return JsonResponse({'error': f'Error processing the file: {str(e)}'}, status=400)

    return JsonResponse({'error': 'No file uploaded'}, status=400)

# Helper function for CSV parsing
def parse_csv(file_data):
    csv_reader = csv.reader(io.StringIO(file_data.decode('utf-8')))
    rows = [row for row in csv_reader]
    return rows


def validate_data(parsed_data, column_types=None):
    
    results = {
        "missing_values": [],
        "invalid_data": [],
        "duplicates": []
    }
    
    # Add this where you parse the CSV data
    data_size_bytes = sys.getsizeof(parsed_data)  # Size of the data in bytes
    num_rows = len(parsed_data)  # Total number of rows (including header)
    num_columns = len(parsed_data[0]) if parsed_data else 0  # Total number of columns

    # Convert size to KB for better readability
    data_size_kb = round(data_size_bytes / 1024, 2)  # Convert bytes to kilobytes
    
    headers = parsed_data[0]

    # Step 1: Check for missing headers
    if column_types:
        missing_headers = [header for header in column_types if header not in headers]
        if missing_headers:
            results['missing_values'].append(f"Missing Headers: {', '.join(missing_headers)}")

    # Step 2: Check for missing values in each row
    for i, row in enumerate(parsed_data[1:], start=2):  # Skip header row, start from row 2
        for col_index, col_value in enumerate(row):
            if not col_value:  # Empty value check
                column_name = headers[col_index]
                results['missing_values'].append(f"Row {i}: Missing value in '{column_name}'")

    # Step 3: Check for invalid data types (e.g., Age should be an int) and special characters
    if column_types:
        for i, row in enumerate(parsed_data[1:], start=2):  # Skip header row, start from row 2
            for col, expected_type in column_types.items():
                if col in headers:
                    col_index = headers.index(col)
                    col_value = row[col_index]

                    # Skip invalid data check if the value is missing
                    if not col_value:
                        continue
                    
                    # Check if it can be converted to the expected type
                    try:
                        if expected_type == 'float':
                            float(col_value)  # Check if it can be converted to float
                        elif expected_type == 'int':
                            int(col_value)  # Check if it can be converted to int
                    except (ValueError, TypeError):
                        results['invalid_data'].append(
                            f"Row {i}: Invalid value in '{col}' ({col_value})"
                        )
                    
                    # Check for special characters (only if it's a string column or specified by column_types)
                    if isinstance(col_value, str) and re.search(r'[^a-zA-Z0-9\s]', col_value):
                        results['invalid_data'].append(
                            f"Row {i}: Special characters found in '{col}' ({col_value})"
                        )

    # Step 4: Check for duplicate rows
    seen = set()
    for i, row in enumerate(parsed_data[1:], start=2):
        if not any(row):  # Skip fully empty rows
            continue
        row_tuple = tuple(row)
        if row_tuple in seen:
            continue  # Ignore this row
        seen.add(row_tuple)


    # Step 5: If no errors, return success message
    if not any(results.values()):  # If no missing, invalid, or duplicate data
        return JsonResponse({
            "status": "success",
            "message": "Validation successful. No issues found."
        })
    
    # Return the JSON response with all validation issues
    return JsonResponse({
        "status": "error",
        "missing_values": results['missing_values'],
        "invalid_data": results['invalid_data'],
        "duplicates": results['duplicates'],
        "data_size": f"{data_size_kb} KB",
        "rows": num_rows,
        "columns": num_columns
    })





@csrf_exempt
 # Ensure CSRF protection is enabled for this view
def check_missing_values(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            df = pd.read_csv(file, on_bad_lines='skip')  # 'on_bad_lines' for better error handling

            # Check for missing values
            missing_values = df.isnull().sum()
            missing_columns = {col: int(count) for col, count in missing_values.items() if count > 0}

            return JsonResponse({'missing_value_columns': missing_columns})
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'})
    else:
        return JsonResponse({'error': 'Invalid request or no file uploaded'})



def handle_missing_values(request):
    if request.method == 'POST':
        # 1️⃣ Get the DataFrame from the session
        df_dict = request.session.get('df', None)
        if df_dict is None:
            return JsonResponse({'error': 'No data available to process.'}, status=400)

        df = pd.DataFrame(df_dict)

        # 2️⃣ Get actions and custom values from the POST request
        actions = request.POST.getlist('missing_data_actions[]')
        custom_values = request.POST.getlist('custom_values[]')

        # Ensure the number of custom values matches the columns with missing data
        missing_columns = [col for col in df.columns if df[col].isnull().any()]
        if len(custom_values) != len(missing_columns):
            return JsonResponse({'error': 'Number of custom values must match the columns with missing values.'}, status=400)

        # 3️⃣ Iterate through columns and apply actions
        for i, col in enumerate(missing_columns):
            action = actions[i]
            custom_value = custom_values[i].strip() if custom_values[i].strip() != '' else None  # Handle empty string as None

            if action == 'drop':
                df = df.dropna(subset=[col])
            elif action == 'custom':
                if custom_value is None:
                    return JsonResponse({'error': f"Custom value for column '{col}' is required."}, status=400)

                # Handle custom value based on the column's data type
                try:
                    # Convert custom value to appropriate type
                    dtype = df[col].dtype

                    if dtype == 'object':  # For string columns
                        df[col] = df[col].fillna(custom_value)
                    elif dtype in ['int64', 'float64']:  # For numeric columns
                        df[col] = df[col].fillna(type(df[col].iloc[0])(custom_value))  # Convert string to numeric type
                    else:
                        return JsonResponse({'error': f"Unsupported column type for column '{col}'"}, status=400)

                except Exception as e:
                    return JsonResponse({'error': f"Error processing custom value for column '{col}': {str(e)}"}, status=400)

        # 4️⃣ Store the cleaned DataFrame in the session
        request.session['file_path'] = file_path  # Store path instead of full DataFrame


        return JsonResponse({'message': 'Missing values handled successfully.', 'data': df.to_dict()})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



@login_required
@csrf_exempt
def remove_duplicates(request):
    if request.method == 'POST':
        # 1️⃣ Get the DataFrame from the session
        df_dict = request.session.get('df', None)
        if df_dict is None:
            return JsonResponse({'error': 'No data available to process.'}, status=400)

        df = pd.DataFrame(df_dict)

        # 2️⃣ Remove duplicate rows
        df_cleaned = df.drop_duplicates()

        # 3️⃣ Save the cleaned DataFrame back to the session (optional, for further operations)
        request.session['df'] = df_cleaned.to_dict()

        # 4️⃣ Return success message and number of duplicates removed
        duplicates_removed = len(df) - len(df_cleaned)  # Calculate the number of duplicates removed
        return JsonResponse({
            'status': 'success',
            'message': f'{duplicates_removed} duplicate row(s) removed.',
            'cleaned_data': df_cleaned.head(5).to_html(classes='table table-striped', index=False)  # Show the first 5 rows as preview
        })

    return JsonResponse({'error': 'Invalid request method or no data available.'}, status=400)















@login_required
def contact_details(request):
    # This view simply renders the contact page
    return render(request, 'datacleaning/contact_details.html')

def settings_view(request):
    return render(request, 'datacleaning/settings.html')

def about_us_view(request):
    return render(request, 'datacleaning/about_us.html')

def change_password_view(request):
    return render(request, 'datacleaning/change_password.html')

def faq_view(request):
    return render(request, 'datacleaning/faq.html')




from django.shortcuts import render
from .models import Notification

def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'notifications.html', {'notifications': user_notifications})

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def send_notification_to_user(user, message):
    """ Save notification to database and send it via WebSocket """
    notification = Notification.objects.create(user=user, message=message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            'type': 'send_notification',
            'message': message
        }
    )


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            # Update the user's password
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('settings')  # Redirect to the settings page or wherever you want
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'datacleaning/change_password.html', {'form': form})