from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
from functools import wraps
import re

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])  # Allow React frontend
app.config['SECRET_KEY'] = 'alumni-connect-secret-key-2024'

# -----------------------------
# Mock Data Stores (In-Memory)
# -----------------------------
users = []
alumni = []
events = []
jobs = []
donations = []
posts = []
messages = []

# -----------------------------
# Helper Functions
# -----------------------------
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def find_user_by_email(email):
    return next((u for u in users if u['email'] == email), None)

def find_alumni_by_id(alumni_id):
    return next((a for a in alumni if a['id'] == alumni_id), None)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Access token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((u for u in users if u['id'] == data['user_id']), None)
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# -----------------------------
# Home & Health Check
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Alumni Connect Backend v1.0 - Running",
        "message": "API for Government Engineering College, Gujarat",
        "endpoints": {
            "auth": ["/api/auth/register", "/api/auth/login"],
            "alumni": ["/api/alumni", "/api/alumni/<id>"],
            "events": ["/api/events", "/api/events/<id>"],
            "jobs": ["/api/jobs", "/api/jobs/<id>"],
            "donations": ["/api/donations", "/api/donations/<id>"],
            "posts": ["/api/posts", "/api/posts/<id>"],
            "messages": ["/api/messages"]
        }
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_counts": {
            "users": len(users),
            "alumni": len(alumni),
            "events": len(events),
            "jobs": len(jobs),
            "donations": len(donations),
            "posts": len(posts),
            "messages": len(messages)
        }
    })

# -----------------------------
# Authentication System
# -----------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validation
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        
        if len(data['password']) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        if find_user_by_email(data['email']):
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Create user
        user = {
            "id": len(users) + 1,
            "email": data['email'].lower(),
            "password": data['password'],  # In production, hash this!
            "name": data['name'],
            "role": data.get('role', 'alumni'),
            "created_at": datetime.now().isoformat()
        }
        users.append(user)
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Remove password from response
        user_response = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_response,
            "token": token
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = find_user_by_email(email)
        if not user or user['password'] != password:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Remove password from response
        user_response = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            "message": "Login successful",
            "user": user_response,
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

# -----------------------------
# Alumni Management
# -----------------------------
@app.route("/api/alumni", methods=["GET", "POST"])
def alumni_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            # Validation
            required_fields = ['name', 'email', 'batch', 'department']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            if not validate_email(data['email']):
                return jsonify({"error": "Invalid email format"}), 400
            
            # Check for duplicate email
            if any(a['email'].lower() == data['email'].lower() for a in alumni):
                return jsonify({"error": "Alumni with this email already exists"}), 409
            
            # Create alumni profile
            alumni_data = {
                "id": len(alumni) + 1,
                "name": data['name'],
                "email": data['email'].lower(),
                "batch": data['batch'],
                "department": data['department'],
                "phone": data.get('phone', ''),
                "current_company": data.get('current_company', ''),
                "current_position": data.get('current_position', ''),
                "location": data.get('location', ''),
                "bio": data.get('bio', ''),
                "linkedin": data.get('linkedin', ''),
                "profile_image": data.get('profile_image', ''),
                "graduation_year": data.get('graduation_year', ''),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            alumni.append(alumni_data)
            
            return jsonify({
                "message": "Alumni profile created successfully",
                "alumni": alumni_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to create alumni profile", "details": str(e)}), 500
    
    # GET request - List all alumni with filters
    try:
        # Query parameters for filtering/searching
        search = request.args.get('search', '').lower()
        batch = request.args.get('batch', '')
        department = request.args.get('department', '')
        company = request.args.get('company', '').lower()
        
        filtered_alumni = alumni.copy()
        
        # Apply filters
        if search:
            filtered_alumni = [a for a in filtered_alumni if 
                             search in a.get('name', '').lower() or 
                             search in a.get('current_company', '').lower()]
        
        if batch:
            filtered_alumni = [a for a in filtered_alumni if str(a.get('batch', '')) == batch]
        
        if department:
            filtered_alumni = [a for a in filtered_alumni if 
                             a.get('department', '').lower() == department.lower()]
        
        if company:
            filtered_alumni = [a for a in filtered_alumni if 
                             company in a.get('current_company', '').lower()]
        
        return jsonify({
            "alumni": filtered_alumni,
            "total": len(filtered_alumni)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch alumni", "details": str(e)}), 500

@app.route("/api/alumni/<int:alumni_id>", methods=["GET", "PUT", "DELETE"])
def alumni_detail(alumni_id):
    try:
        alum = find_alumni_by_id(alumni_id)
        if not alum:
            return jsonify({"error": "Alumni not found"}), 404
        
        if request.method == "GET":
            return jsonify({"alumni": alum}), 200
        
        if request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            # Validate email if being updated
            if 'email' in data and not validate_email(data['email']):
                return jsonify({"error": "Invalid email format"}), 400
            
            # Check for duplicate email (excluding current alumni)
            if 'email' in data:
                existing = next((a for a in alumni if a['email'].lower() == data['email'].lower() and a['id'] != alumni_id), None)
                if existing:
                    return jsonify({"error": "Email already exists for another alumni"}), 409
            
            # Update alumni data
            for key, value in data.items():
                if key != 'id':  # Don't allow ID updates
                    alum[key] = value
            alum['updated_at'] = datetime.now().isoformat()
            
            return jsonify({
                "message": "Alumni profile updated successfully",
                "alumni": alum
            }), 200
        
        if request.method == "DELETE":
            alumni.remove(alum)
            return jsonify({"message": "Alumni profile deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": "Operation failed", "details": str(e)}), 500

# -----------------------------
# Event Management
# -----------------------------
@app.route("/api/events", methods=["GET", "POST"])
def event_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            required_fields = ['title', 'description', 'date', 'location']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            event_data = {
                "id": len(events) + 1,
                "title": data['title'],
                "description": data['description'],
                "date": data['date'],
                "time": data.get('time', ''),
                "location": data['location'],
                "event_type": data.get('event_type', 'general'),
                "max_attendees": data.get('max_attendees', None),
                "registration_required": data.get('registration_required', False),
                "organizer": data.get('organizer', ''),
                "contact_email": data.get('contact_email', ''),
                "image_url": data.get('image_url', ''),
                "status": "upcoming",
                "attendees": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            events.append(event_data)
            
            return jsonify({
                "message": "Event created successfully",
                "event": event_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to create event", "details": str(e)}), 500
    
    # GET request
    try:
        event_type = request.args.get('type', '')
        status = request.args.get('status', '')
        
        filtered_events = events.copy()
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.get('event_type', '') == event_type]
        
        if status:
            filtered_events = [e for e in filtered_events if e.get('status', '') == status]
        
        return jsonify({
            "events": filtered_events,
            "total": len(filtered_events)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch events", "details": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["GET", "PUT", "DELETE"])
def event_detail(event_id):
    try:
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        
        if request.method == "GET":
            return jsonify({"event": event}), 200
        
        if request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            for key, value in data.items():
                if key != 'id':
                    event[key] = value
            event['updated_at'] = datetime.now().isoformat()
            
            return jsonify({
                "message": "Event updated successfully",
                "event": event
            }), 200
        
        if request.method == "DELETE":
            events.remove(event)
            return jsonify({"message": "Event deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": "Operation failed", "details": str(e)}), 500

# -----------------------------
# Job Portal
# -----------------------------
@app.route("/api/jobs", methods=["GET", "POST"])
def job_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            required_fields = ['title', 'company', 'description', 'location']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            job_data = {
                "id": len(jobs) + 1,
                "title": data['title'],
                "company": data['company'],
                "description": data['description'],
                "location": data['location'],
                "job_type": data.get('job_type', 'full-time'),
                "experience_level": data.get('experience_level', 'entry'),
                "salary_range": data.get('salary_range', ''),
                "requirements": data.get('requirements', ''),
                "contact_email": data.get('contact_email', ''),
                "application_url": data.get('application_url', ''),
                "posted_by": data.get('posted_by', ''),
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "expires_at": data.get('expires_at', '')
            }
            jobs.append(job_data)
            
            return jsonify({
                "message": "Job posted successfully",
                "job": job_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to post job", "details": str(e)}), 500
    
    # GET request
    try:
        job_type = request.args.get('type', '')
        location = request.args.get('location', '').lower()
        company = request.args.get('company', '').lower()
        
        filtered_jobs = jobs.copy()
        
        if job_type:
            filtered_jobs = [j for j in filtered_jobs if j.get('job_type', '') == job_type]
        
        if location:
            filtered_jobs = [j for j in filtered_jobs if location in j.get('location', '').lower()]
        
        if company:
            filtered_jobs = [j for j in filtered_jobs if company in j.get('company', '').lower()]
        
        return jsonify({
            "jobs": filtered_jobs,
            "total": len(filtered_jobs)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch jobs", "details": str(e)}), 500

@app.route("/api/jobs/<int:job_id>", methods=["GET", "PUT", "DELETE"])
def job_detail(job_id):
    try:
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        if request.method == "GET":
            return jsonify({"job": job}), 200
        
        if request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            for key, value in data.items():
                if key != 'id':
                    job[key] = value
            job['updated_at'] = datetime.now().isoformat()
            
            return jsonify({
                "message": "Job updated successfully",
                "job": job
            }), 200
        
        if request.method == "DELETE":
            jobs.remove(job)
            return jsonify({"message": "Job deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": "Operation failed", "details": str(e)}), 500

# -----------------------------
# Donation Portal
# -----------------------------
@app.route("/api/donations", methods=["GET", "POST"])
def donation_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            required_fields = ['donor_name', 'amount', 'purpose']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({"error": "Amount must be greater than 0"}), 400
            except ValueError:
                return jsonify({"error": "Invalid amount format"}), 400
            
            donation_data = {
                "id": len(donations) + 1,
                "donor_name": data['donor_name'],
                "donor_email": data.get('donor_email', ''),
                "amount": amount,
                "currency": data.get('currency', 'INR'),
                "purpose": data['purpose'],
                "message": data.get('message', ''),
                "anonymous": data.get('anonymous', False),
                "payment_method": data.get('payment_method', ''),
                "transaction_id": data.get('transaction_id', ''),
                "status": "completed",
                "created_at": datetime.now().isoformat()
            }
            donations.append(donation_data)
            
            return jsonify({
                "message": "Donation recorded successfully",
                "donation": donation_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to record donation", "details": str(e)}), 500
    
    # GET request
    try:
        purpose = request.args.get('purpose', '')
        
        filtered_donations = donations.copy()
        
        if purpose:
            filtered_donations = [d for d in filtered_donations if d.get('purpose', '') == purpose]
        
        # Hide anonymous donors' details
        for donation in filtered_donations:
            if donation.get('anonymous', False):
                donation['donor_name'] = 'Anonymous'
                donation['donor_email'] = ''
        
        total_amount = sum(d['amount'] for d in filtered_donations)
        
        return jsonify({
            "donations": filtered_donations,
            "total": len(filtered_donations),
            "total_amount": total_amount
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch donations", "details": str(e)}), 500

@app.route("/api/donations/<int:donation_id>", methods=["GET"])
def donation_detail(donation_id):
    try:
        donation = next((d for d in donations if d['id'] == donation_id), None)
        if not donation:
            return jsonify({"error": "Donation not found"}), 404
        
        return jsonify({"donation": donation}), 200
    
    except Exception as e:
        return jsonify({"error": "Operation failed", "details": str(e)}), 500

# -----------------------------
# Posts/Feed
# -----------------------------
@app.route("/api/posts", methods=["GET", "POST"])
def post_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            required_fields = ['author_name', 'content']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            post_data = {
                "id": len(posts) + 1,
                "author_name": data['author_name'],
                "author_email": data.get('author_email', ''),
                "author_batch": data.get('author_batch', ''),
                "content": data['content'],
                "post_type": data.get('post_type', 'general'),
                "image_url": data.get('image_url', ''),
                "likes": 0,
                "comments": [],
                "tags": data.get('tags', []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            posts.append(post_data)
            
            return jsonify({
                "message": "Post created successfully",
                "post": post_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to create post", "details": str(e)}), 500
    
    # GET request
    try:
        post_type = request.args.get('type', '')
        author = request.args.get('author', '').lower()
        
        filtered_posts = posts.copy()
        
        if post_type:
            filtered_posts = [p for p in filtered_posts if p.get('post_type', '') == post_type]
        
        if author:
            filtered_posts = [p for p in filtered_posts if author in p.get('author_name', '').lower()]
        
        # Sort by creation date (newest first)
        filtered_posts = sorted(filtered_posts, key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            "posts": filtered_posts,
            "total": len(filtered_posts)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch posts", "details": str(e)}), 500

@app.route("/api/posts/<int:post_id>", methods=["GET", "PUT", "DELETE"])
def post_detail(post_id):
    try:
        post = next((p for p in posts if p['id'] == post_id), None)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        if request.method == "GET":
            return jsonify({"post": post}), 200
        
        if request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            for key, value in data.items():
                if key not in ['id', 'created_at']:
                    post[key] = value
            post['updated_at'] = datetime.now().isoformat()
            
            return jsonify({
                "message": "Post updated successfully",
                "post": post
            }), 200
        
        if request.method == "DELETE":
            posts.remove(post)
            return jsonify({"message": "Post deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": "Operation failed", "details": str(e)}), 500

# -----------------------------
# Messaging System
# -----------------------------
@app.route("/api/messages", methods=["GET", "POST"])
def message_list():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            required_fields = ['sender_email', 'recipient_email', 'content']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400
            
            message_data = {
                "id": len(messages) + 1,
                "sender_email": data['sender_email'],
                "recipient_email": data['recipient_email'],
                "content": data['content'],
                "message_type": data.get('message_type', 'direct'),
                "group_id": data.get('group_id', None),
                "read": False,
                "created_at": datetime.now().isoformat()
            }
            messages.append(message_data)
            
            return jsonify({
                "message": "Message sent successfully",
                "message_data": message_data
            }), 201
            
        except Exception as e:
            return jsonify({"error": "Failed to send message", "details": str(e)}), 500
    
    # GET request
    try:
        user_email = request.args.get('user_email', '').lower()
        message_type = request.args.get('type', '')
        
        if not user_email:
            return jsonify({"error": "user_email parameter is required"}), 400
        
        filtered_messages = []
        for msg in messages:
            if (msg.get('sender_email', '').lower() == user_email or 
                msg.get('recipient_email', '').lower() == user_email):
                if not message_type or msg.get('message_type', '') == message_type:
                    filtered_messages.append(msg)
        
        # Sort by creation date (newest first)
        filtered_messages = sorted(filtered_messages, key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            "messages": filtered_messages,
            "total": len(filtered_messages)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch messages", "details": str(e)}), 500

# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    print("🚀 Alumni Connect Backend Starting...")
    print("📍 Government Engineering College, Gujarat")
    print("🌐 Server running on http://localhost:5000")
    print("📖 API Documentation available at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)