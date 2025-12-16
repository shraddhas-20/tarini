from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3
import os
from datetime import datetime
import bcrypt
import re

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', "tarini_secret_key_2024")

# Database setup
DATABASE = 'tarini_safety.db'

def init_db():
    """Initialize the database with required tables"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Users tablerun
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                age INTEGER,
                password TEXT NOT NULL,
                emergency_contact TEXT,
                emergency_phone TEXT,
                newsletter INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Emergency contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # SOS alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sos_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                location TEXT,
                message TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Voice notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_contacts(user_id):
    """Get all emergency contacts for a user"""
    conn = get_db_connection()
    contacts = conn.execute(
        'SELECT * FROM emergency_contacts WHERE user_id = ? ORDER BY created_at DESC', 
        (user_id,)
    ).fetchall()
    conn.close()
    return contacts

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    return len(phone_digits) >= 10

# Initialize database on startup
init_db()

@app.route('/')
def home():
    """Home page"""
    user_name = session.get('user_name') if 'user_id' in session else None
    return render_template('index.html', user_name=user_name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        age = request.form.get('age')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')
        emergency_contact = request.form.get('emergencyContact', '').strip()
        emergency_phone = request.form.get('emergencyPhone', '').strip()
        newsletter = 1 if request.form.get('newsletter') else 0
        
        # Validation
        if not all([first_name, last_name, email, password]):
            flash('All required fields must be filled!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if get_user_by_email(email):
            flash('Email already registered! Please login instead.', 'error')
            return render_template('register.html')
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user into database
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO users (first_name, last_name, email, phone, age, password, 
                                 emergency_contact, emergency_phone, newsletter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, phone, age, hashed_password, 
                  emergency_contact, emergency_phone, newsletter))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html')
        
        user = get_user_by_email(email)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = f"{user['first_name']} {user['last_name']}"
            flash(f'Welcome back, {user["first_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    # Get user's emergency contacts count
    contacts = get_user_contacts(session['user_id'])
    contact_count = len(contacts)
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         contact_count=contact_count)

@app.route('/manage-contacts')
def manage_contacts():
    """Manage emergency contacts page"""
    if 'user_id' not in session:
        flash('Please login to manage contacts.', 'error')
        return redirect(url_for('login'))
    
    contacts = get_user_contacts(session['user_id'])
    return render_template('manage_contacts_simple.html', contacts=contacts)

@app.route('/add-contact', methods=['POST'])
def add_contact_form():
    """Add new emergency contact"""
    if 'user_id' not in session:
        flash('Please login to add contacts.', 'error')
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    relation = request.form.get('relation', '').strip()
    
    # Validation
    if not all([name, phone]):
        flash('Name and phone number are required!', 'error')
        return redirect(url_for('manage_contacts'))
    
    if not validate_phone(phone):
        flash('Please enter a valid phone number!', 'error')
        return redirect(url_for('manage_contacts'))
    
    # Check if contact already exists for this user
    conn = get_db_connection()
    existing_contact = conn.execute(
        'SELECT * FROM emergency_contacts WHERE user_id = ? AND phone = ?', 
        (session['user_id'], phone)
    ).fetchone()
    
    if existing_contact:
        flash('This phone number is already in your emergency contacts!', 'error')
        conn.close()
        return redirect(url_for('manage_contacts'))
    
    # Add the contact
    try:
        conn.execute(
            'INSERT INTO emergency_contacts (user_id, name, phone, relation) VALUES (?, ?, ?, ?)',
            (session['user_id'], name, phone, relation)
        )
        conn.commit()
        flash(f'Successfully added {name} to your emergency contacts!', 'success')
    except Exception as e:
        flash(f'Failed to add contact: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage_contacts'))

@app.route('/delete-contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    """Delete emergency contact"""
    if 'user_id' not in session:
        flash('Please login to delete contacts.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if contact belongs to current user
    contact = conn.execute(
        'SELECT * FROM emergency_contacts WHERE id = ? AND user_id = ?', 
        (contact_id, session['user_id'])
    ).fetchone()
    
    if not contact:
        flash('Contact not found or you do not have permission to delete it.', 'error')
        conn.close()
        return redirect(url_for('manage_contacts'))
    
    # Delete the contact
    try:
        conn.execute('DELETE FROM emergency_contacts WHERE id = ?', (contact_id,))
        conn.commit()
        flash(f'Successfully removed {contact["name"]} from your emergency contacts.', 'success')
    except Exception as e:
        flash(f'Failed to delete contact: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage_contacts'))

@app.route('/sos', methods=['POST'])
def trigger_sos():
    """Trigger SOS alert"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    location = request.form.get('location', 'Location not available')
    message = request.form.get('message', 'Emergency SOS triggered')
    
    # Save SOS alert to database
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO sos_alerts (user_id, location, message) VALUES (?, ?, ?)',
            (session['user_id'], location, message)
        )
        conn.commit()
        
        # Get user's emergency contacts
        contacts = get_user_contacts(session['user_id'])
        
        # In a real app, you would send SMS/calls to emergency contacts here
        # For now, we'll just flash a message
        contact_count = len(contacts)
        if contact_count > 0:
            flash(f'🚨 SOS Alert sent to {contact_count} emergency contacts!', 'success')
        else:
            flash('🚨 SOS Alert logged! Please add emergency contacts for better safety.', 'warning')
            
    except Exception as e:
        flash(f'Failed to send SOS alert: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/voice-notes')
def voice_notes_page():
    """Voice notes management page"""
    if 'user_id' not in session:
        flash('Please login to access voice notes.', 'error')
        return redirect(url_for('login'))
    
    return render_template('voice_notes.html', user_name=session.get('user_name'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# API endpoints for AJAX requests
@app.route('/api/contacts')
def api_contacts():
    """API endpoint to get contacts as JSON"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    contacts = get_user_contacts(session['user_id'])
    contacts_list = []
    for contact in contacts:
        contacts_list.append({
            'id': contact['id'],
            'name': contact['name'],
            'phone': contact['phone'],
            'relation': contact['relation']
        })
    
    return jsonify({'contacts': contacts_list})

@app.route('/upload-voice-note', methods=['POST'])
def upload_voice_note():
    """Upload and save voice note audio file"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    if 'voice_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['voice_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is audio
    allowed_extensions = {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'webm'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid audio file format. Please use mp3, wav, ogg, m4a, aac, or webm'}), 400
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join('uploads', 'voice_notes')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"voice_note_{session['user_id']}_{timestamp}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Save file
        file.save(file_path)
        
        # Save to database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO voice_notes (user_id, filename, file_path, created_at)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], file.filename, file_path, datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Voice note uploaded successfully!', 'filename': filename})
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload voice note: {str(e)}'}), 500

@app.route('/get-voice-notes')
def get_voice_notes():
    """Get user's uploaded voice notes"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    conn = get_db_connection()
    voice_notes = conn.execute(
        'SELECT * FROM voice_notes WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    notes_list = []
    for note in voice_notes:
        notes_list.append({
            'id': note['id'],
            'filename': note['filename'],
            'file_path': note['file_path'],
            'created_at': note['created_at']
        })
    
    return jsonify({'voice_notes': notes_list})

@app.route('/play-voice-note/<int:note_id>')
def play_voice_note(note_id):
    """Serve voice note audio file"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    conn = get_db_connection()
    note = conn.execute(
        'SELECT * FROM voice_notes WHERE id = ? AND user_id = ?',
        (note_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not note:
        return jsonify({'error': 'Voice note not found'}), 404
    
    try:
        # Check if file exists
        if not os.path.exists(note['file_path']):
            return jsonify({'error': 'Voice note file not found on server'}), 404
        
        # Get the file extension to set proper MIME type
        file_extension = note['file_path'].split('.')[-1].lower()
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'aac': 'audio/aac',
            'webm': 'audio/webm'
        }
        mime_type = mime_types.get(file_extension, 'audio/mpeg')
        
        def generate():
            with open(note['file_path'], 'rb') as f:
                data = f.read(1024)
                while data:
                    yield data
                    data = f.read(1024)
        
        response = Response(generate(), mimetype=mime_type)
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', 'no-cache')
        response.headers.add('Access-Control-Allow-Origin', '*')
        
        return response
        
    except FileNotFoundError:
        return jsonify({'error': 'Voice note file not found'}), 404
    except Exception as e:
        print(f"Error serving voice note: {str(e)}")  # Debug print
        return jsonify({'error': f'Failed to serve voice note: {str(e)}'}), 500

@app.route('/delete-voice-note/<int:note_id>', methods=['POST'])
def delete_voice_note(note_id):
    """Delete voice note"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    conn = get_db_connection()
    note = conn.execute(
        'SELECT * FROM voice_notes WHERE id = ? AND user_id = ?',
        (note_id, session['user_id'])
    ).fetchone()
    
    if not note:
        conn.close()
        return jsonify({'error': 'Voice note not found'}), 404
    
    try:
        # Delete file from filesystem
        if os.path.exists(note['file_path']):
            os.remove(note['file_path'])
        
        # Delete from database
        conn.execute('DELETE FROM voice_notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Voice note deleted successfully'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Failed to delete voice note: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database when app starts
    init_db()
    # Use environment port for Railway deployment
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
