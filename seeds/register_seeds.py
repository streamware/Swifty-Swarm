# Database seeding for microservices
# Generated with Google Gemini
# I'll keep updating it with latest schema changes
import requests
import json
import random
import os
import time
import argparse

from faker import Faker
from jwt import decode
import mimetypes

AUTH_SERVICE_URL = 'http://localhost/auth/api/register'
LOGIN_SERVICE_URL = 'http://localhost/auth/api/login'
MEDIA_SERVICE_UPLOAD_URL = 'http://localhost/media-service/api/v1/user-profile-photo'
USER_SERVICE_SET_DESCRIPTION_URL = 'http://localhost/user-service/users/set-description'

FIXED_PASSWORD = "45632111"
FIXED_DEVICE_FINGERPRINT = "test_device_fingerprint_qq"
FIXED_USER_AGENT = "test_user_agent_qqq"

PROFILE_PHOTO_FILENAMES = [
    "avatar-1.png",
    "avatar-2.png",
    "avatar-3.jpg",
    "avatar-4.jpg",
    "avatar-5.jpeg"
]

fake = Faker('en_US')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_user_data(is_female: bool = False, counter: int = 0):
    """
    Generates a single user's data (username, email, password).
    Includes a counter to help ensure uniqueness for bulk seeding.
    """
    if is_female:
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name_male()

    username = f"{first_name.lower().replace(' ', '')}{random.randint(100, 999)}{counter}"
    email = f"{username}@gmail.com"

    return {
        "username": username,
        "email": email,
        "password": FIXED_PASSWORD
    }


def login_user(email: str, password: str):
    """
    Logs in a user and returns their access token and user ID.
    """
    login_payload = json.dumps({
        "email": email,
        "password": password,
        "deviceFingerprint": FIXED_DEVICE_FINGERPRINT,
        "userAgent": FIXED_USER_AGENT
    })
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(LOGIN_SERVICE_URL, headers=headers, data=login_payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        login_response_data = response.json()
        access_token = login_response_data.get("access_token")

        # Extract user ID. Assuming it's directly available as 'id' or 'sub' in the response,
        # or can be decoded from the access_token.
        user_id = login_response_data.get("id")

        if not user_id and access_token:
            # Fallback: try to decode JWT to get 'sub' or 'id'
            try:
                # For seeding purposes, we decode without verifying the signature for simplicity.
                # WARNING: In production code, always verify JWTs with the correct public key!
                decoded_token = decode(access_token, options={"verify_signature": False})
                user_id = decoded_token.get("sub") or decoded_token.get("id")
            except Exception as e:
                print(f"Warning: Could not decode access token to get user ID: {e}")

        if not access_token or not user_id:
            raise ValueError("Access token or User ID not found in login response.")

        return access_token, user_id

    except requests.exceptions.RequestException as e:
        print(f"   Login failed for {email}. Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"     Login Response Status: {e.response.status_code}")
            print(f"     Login Response Body: {e.response.text}")
        raise # Re-raise to be caught by the main loop
    except ValueError as e:
        print(f"   Login data error for {email}: {e}")
        raise # Re-raise to be caught by the main loop


def upload_profile_photo(access_token: str, user_id: str, photo_path: str):
    """
    Uploads a profile photo for a user using their access token and user ID.
    """
    if not os.path.exists(photo_path):
        print(f"WARNING: Photo file not found for upload: {photo_path}")
        return False

    # Determine MIME type more robustly
    mime_type, _ = mimetypes.guess_type(photo_path)
    if mime_type is None:
        mime_type = 'application/octet-stream' # Fallback generic binary

    with open(photo_path, 'rb') as f:
        # 'file' is the name of the form field expected by the server for the file upload.
        files = {'file': (os.path.basename(photo_path), f, mime_type)}
        headers = {
            'X-USER-ID': user_id,
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.post(MEDIA_SERVICE_UPLOAD_URL, headers=headers, files=files)
            response.raise_for_status()

            print(f"   [UPLOAD] Photo '{os.path.basename(photo_path)}' successful for user {user_id}. Status: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"   [UPLOAD] Photo '{os.path.basename(photo_path)}' failed for user {user_id}. Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"     Upload Response Status: {e.response.status_code}")
                print(f"     Upload Response Body: {e.response.text}")
            print(f"     Common reasons for 400 Bad Request on file uploads:")
            print(f"     - Media service has specific image requirements (e.g., min/max dimensions, file size).")
            print(f"     - The image file might be corrupted or not a valid image.")
            print(f"     - The 'X-USER-ID' ({user_id}) might not be recognized by the media service yet (eventual consistency).")
            print(f"     - **Check your media service's logs for detailed error messages!**")
            return False
        except Exception as e:
            print(f"   [UPLOAD] An unexpected error occurred during photo upload for user {user_id}: {e}")
            return False


def set_user_description(access_token: str, user_id: str, description: str):
    """
    Sets a description for a user.
    """
    description_payload = json.dumps({"description": description})
    headers = {
        'X-USER-ID': user_id,
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.post(USER_SERVICE_SET_DESCRIPTION_URL, headers=headers, data=description_payload)
        response.raise_for_status()

        print(f"   [DESCRIPTION] Description set successful for user {user_id}. Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   [DESCRIPTION] Description set failed for user {user_id}. Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"     Description Response Status: {e.response.status_code}")
            print(f"     Description Response Body: {e.response.text}")
        print(f"     Common reasons for description set failure:")
        print(f"     - User service might have specific validation rules for description content or length.")
        print(f"     - User ID might not be recognized or authorized.")
        print(f"     - **Check your user service's logs for detailed error messages!**")
        return False
    except Exception as e:
        print(f"   [DESCRIPTION] An unexpected error occurred during description set for user {user_id}: {e}")
        return False


# --- Main Seeding Logic ---

def seed_users(num_users: int):
    """
    Seeds a specified number of users: registers, logs in, uploads photos, and sets description.
    """
    print(f"Starting to seed {num_users} users.")
    print(f"Registration URL: {AUTH_SERVICE_URL}")
    print(f"Login URL: {LOGIN_SERVICE_URL}")
    print(f"Photo Upload URL: {MEDIA_SERVICE_UPLOAD_URL}")
    print(f"Description Set URL: {USER_SERVICE_SET_DESCRIPTION_URL}")

    # Check if all required profile photo files exist
    all_photos_exist = True
    for filename in PROFILE_PHOTO_FILENAMES:
        photo_path = os.path.join(SCRIPT_DIR, filename)
        if not os.path.exists(photo_path):
            print(f"ERROR: Required profile photo file not found: {photo_path}. Please ensure it exists.")
            all_photos_exist = False
    if not all_photos_exist:
        return

    successful_registrations = 0
    successful_logins = 0
    successful_photo_uploads = 0
    successful_description_sets = 0

    for i in range(num_users):
        print(f"\n--- Processing User {i+1}/{num_users} ---")
        is_female = (i % 2 == 0)
        user_data = generate_user_data(is_female=is_female, counter=i)
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']

        access_token = None
        user_id = None

        try:
            # --- Step 1: Register User ---
            register_payload = json.dumps(user_data)
            register_headers = {'Content-Type': 'application/json'}
            response = requests.post(AUTH_SERVICE_URL, headers=register_headers, data=register_payload)
            response.raise_for_status()

            print(f"   [REGISTER] Successfully registered: {username} (Status: {response.status_code})")
            successful_registrations += 1

            # --- Step 2: Login User ---
            # Introduce a small delay to allow services to propagate user creation if necessary
            # time.sleep(0.5)
            access_token, user_id = login_user(email, password)
            print(f"   [LOGIN] Successfully logged in {email}. User ID: {user_id}")
            successful_logins += 1

            # Shuffle the PROFILE_PHOTO_FILENAMES list for this user
            shuffled_photos = PROFILE_PHOTO_FILENAMES.copy()  # Create a copy to avoid modifying the original
            random.shuffle(shuffled_photos)

            # --- Step 3: Upload Multiple Profile Photos ---
            photos_uploaded_count = 0
            for filename in shuffled_photos:
                photo_path = os.path.join(SCRIPT_DIR, filename)
                if upload_profile_photo(access_token, user_id, photo_path):
                    photos_uploaded_count += 1
                # Optional: Add a small delay between uploads if your media service has rate limits
                # time.sleep(0.1)

            if photos_uploaded_count == len(PROFILE_PHOTO_FILENAMES):
                successful_photo_uploads += 1
                print(f"   [UPLOAD] All {photos_uploaded_count} photos uploaded for user {user_id}.")
            else:
                print(f"   [UPLOAD] Only {photos_uploaded_count}/{len(PROFILE_PHOTO_FILENAMES)} photos uploaded for user {user_id}.")


            # --- Step 4: Set User Description ---
            # Generate a unique description for each user
            description_text = f"Hello! I am {username}. This is my auto-generated description for user {user_id}."
            if set_user_description(access_token, user_id, description_text):
                successful_description_sets += 1

        except requests.exceptions.RequestException as e:
            print(f"   [ERROR] Registration or subsequent step failed for {username}. Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"     Response Status: {e.response.status_code}")
                print(f"     Response Body: {e.response.text}")
        except Exception as e:
            print(f"   [ERROR] An unexpected error occurred during user {username} seeding: {e}")
            if access_token:
                print(f"     Access Token was: {access_token}")
            if user_id:
                print(f"     User ID was: {user_id}")


    print(f"\n--- Seeding Complete ---")
    print(f"Total users attempted: {num_users}")
    print(f"Successful registrations: {successful_registrations}")
    print(f"Successful logins: {successful_logins}")
    print(f"Successful photo uploads (all for a user): {successful_photo_uploads}")
    print(f"Successful description sets: {successful_description_sets}")


# --- Execute the seeding ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed users for microservices")
    parser.add_argument("num_users", type=int, nargs='?', default=10, help="Number of users to generate (default: 10)")
    args = parser.parse_args()
    seed_users(args.num_users)

