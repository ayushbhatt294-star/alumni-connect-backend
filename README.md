# Alumni Connect Platform - Backend API

## 🎯 Hackathon Prototype for Government Engineering College, Gujarat

### ✅ Complete Backend Implementation
All core features implemented and ready for integration:
- **Authentication System** (Register/Login with JWT tokens)
- **Alumni Management** (CRUD operations with search & filters)
- **Event Management** (Create, list, update events)
- **Job Portal** (Post and manage job opportunities)
- **Donation System** (Record and track donations)
- **Posts/Feed System** (Alumni can share updates)
- **Messaging System** (Direct and group messaging)

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend server
python app.py
```

**Server will run on:** `http://localhost:5000`

Visit `http://localhost:5000` for API documentation

### 📡 Complete API Endpoints

#### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

#### **Alumni Management**
- `GET /api/alumni` - List all alumni (supports search: `?search=name&batch=2021`)
- `POST /api/alumni` - Create new alumni profile
- `GET /api/alumni/<id>` - Get specific alumni details
- `PUT /api/alumni/<id>` - Update alumni profile
- `DELETE /api/alumni/<id>` - Delete alumni profile

#### **Event Management**
- `GET /api/events` - List all events (supports filters: `?type=workshop&status=upcoming`)
- `POST /api/events` - Create new event
- `GET /api/events/<id>` - Get specific event
- `PUT /api/events/<id>` - Update event
- `DELETE /api/events/<id>` - Delete event

#### **Job Portal**
- `GET /api/jobs` - List all jobs (supports filters: `?type=full-time&location=mumbai`)
- `POST /api/jobs` - Post new job
- `GET /api/jobs/<id>` - Get specific job
- `PUT /api/jobs/<id>` - Update job
- `DELETE /api/jobs/<id>` - Delete job

#### **Donation System**
- `GET /api/donations` - List all donations
- `POST /api/donations` - Record new donation
- `GET /api/donations/<id>` - Get specific donation

#### **Posts/Feed**
- `GET /api/posts` - List all posts (supports filters: `?type=achievement&author=john`)
- `POST /api/posts` - Create new post
- `GET /api/posts/<id>` - Get specific post
- `PUT /api/posts/<id>` - Update post
- `DELETE /api/posts/<id>` - Delete post

#### **Messaging**
- `GET /api/messages` - Get user messages (`?user_email=user@example.com`)
- `POST /api/messages` - Send new message

#### **Utility**
- `GET /` - API documentation and health check
- `GET /api/health` - Detailed health check with data counts

### 🔧 For Frontend Team

#### **CORS Configuration**
✅ CORS enabled for `localhost:3000` and `localhost:3001`

#### **Example Frontend Integration:**
```javascript
// Login Example
const login = async (email, password) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data; // Returns: { token, user, message }
};

// Get Alumni with Search
const getAlumni = async (searchTerm = '') => {
  const url = `http://localhost:5000/api/alumni${searchTerm ? `?search=${searchTerm}` : ''}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.alumni; // Returns array of alumni
};

// Create New Alumni
const createAlumni = async (alumniData) => {
  const response = await fetch('http://localhost:5000/api/alumni', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(alumniData)
  });
  return await response.json();
};
```

#### **Required Data Formats:**

**Alumni Creation:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "batch": "2021",
  "department": "Computer Science",
  "phone": "9876543210",
  "current_company": "Tech Corp",
  "current_position": "Software Engineer"
}
```

**Event Creation:**
```json
{
  "title": "Alumni Meetup 2024",
  "description": "Annual networking event",
  "date": "2024-12-15",
  "time": "6:00 PM",
  "location": "College Auditorium",
  "event_type": "networking"
}
```

### 🗄️ For Database Team

#### **Current Implementation:**
- Uses **in-memory storage** (Python lists)
- Perfect for hackathon development and testing
- All data structures are ready for database migration

#### **Database Integration Guide:**
Replace these lines in `app.py`:

```python
# Current (Mock Data)
alumni = []
alumni.append(data)

# Replace with (Database)
from your_database import db
db.alumni.insert(data)
```

#### **Data Models Structure:**
- **Users:** id, email, password, name, role, created_at
- **Alumni:** id, name, email, batch, department, phone, company, position, etc.
- **Events:** id, title, description, date, time, location, type, attendees
- **Jobs:** id, title, company, description, location, type, salary_range
- **Donations:** id, donor_name, amount, purpose, anonymous, created_at
- **Posts:** id, author_name, content, type, likes, comments, created_at
- **Messages:** id, sender_email, recipient_email, content, created_at

### 🚨 Error Handling
- ✅ Comprehensive input validation
- ✅ Proper HTTP status codes
- ✅ Detailed error messages
- ✅ Duplicate prevention
- ✅ Email format validation

### 🔒 Security Features
- ✅ JWT token authentication
- ✅ Password validation (6+ characters)
- ✅ Email uniqueness checks
- ✅ Input sanitization

### 📊 Response Format
All endpoints return consistent JSON format:
```json
{
  "message": "Operation successful",
  "data": { ... },
  "error": "Error description (if any)"
}
```

### 🧪 Testing the APIs
Use tools like Postman, Thunder Client, or curl:

```bash
# Test API health
curl http://localhost:5000/api/health

# Test alumni list
curl http://localhost:5000/api/alumni

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 🎉 Status: ✅ READY FOR INTEGRATION

**Backend Team:** Complete ✅  
**Frontend Team:** Ready to integrate ✅  
**Database Team:** Ready for DB connection ✅  
**Demo Ready:** Fully functional ✅

### 📞 Support
For any integration issues, refer to the API documentation at `http://localhost:5000` when the server is running.