# TrustLine Project

## Overview
TrustLine is a Cyber Crime Reporting and Security System designed to provide a secure and confidential platform for victims of cyberbullying, online harassment, and privacy violations. The system facilitates efficient reporting, case management, and support for victims while ensuring data privacy and security.

---

## Key Features

### Backend
1. **Complaint Management**:
   - Users can file complaints manually or via a chatbot.
   - Complaints include victim details, incident descriptions, and evidence uploads.
   - Complaints are categorized and prioritized (e.g., pending, under review, closed).

2. **Role-Based Access**:
   - Roles include `user`, `admin`, and `guardian`.
   - Each role has specific permissions for accessing and managing data.

3. **Evidence Handling**:
   - Users can upload evidence files with type and size validation.
   - Evidence is stored locally in a secure directory.

4. **Messaging and Notifications**:
   - Users and admins can exchange messages related to complaints.
   - Notifications are stored in the database for key actions (e.g., complaint updates).

5. **Audit Logging**:
   - Tracks actions like login, complaint creation, status changes, and evidence uploads.

6. **Chatbot Integration**:
   - A chatbot guides users through the complaint filing process.
   - It uses machine learning (ML) for distress detection and incident classification.

7. **Admin Dashboard**:
   - Admins review complaints, assign priorities, and communicate with users.
   - Internal notes and status updates are supported.

### Frontend
1. **User Dashboard**:
   - Displays complaint statistics (e.g., total, pending, closed).
   - Allows users to view and manage their complaints.

2. **Manual Report Form**:
   - Users can file complaints directly through a form.
   - Includes fields for victim details, incident description, and evidence uploads.

3. **Chatbot Interface**:
   - Provides a conversational interface for guided complaint filing.

4. **Navigation and UI**:
   - Modern, responsive design using Next.js and ShadCN/UI components.
   - Includes a navbar, footer, and hero section for easy navigation.

---

## Technical Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **File Storage**: Local directory for evidence uploads
- **ML Integration**: Chatbot uses ML models for distress detection and incident classification.

### Frontend
- **Framework**: Next.js (React-based)
- **UI Components**: ShadCN/UI, Radix UI
- **State Management**: React hooks
- **API Integration**: Fetches data from the backend for dynamic updates.

---

## Models

### Complaint Model
- **Fields**:
  - `case_id`: Unique identifier for the complaint.
  - `title`, `category`, `incident_description`: Details of the incident.
  - `victim_name`, `victim_phone`, `victim_address`: Victim details.
  - `status`, `priority`, `source_type`: Complaint metadata.
  - `reporter_id`, `assigned_admin_id`: Relationships to users.
  - `evidence_items`, `messages`: Relationships to evidence and messages.

### User Model
- **Fields**:
  - `full_name`, `email`, `phone_number`: User details.
  - `password_hash`: Encrypted password.
  - `role`: User role (e.g., admin, user).
  - `complaints`, `assigned_complaints`: Relationships to complaints.

### Chatbot Models
- **ChatSession**:
  - Tracks chatbot sessions, including draft data and submission status.
  - Fields: `session_id`, `user_id`, `is_submitted`, `draft_data`.
- **ChatSessionMessage**:
  - Stores messages exchanged during chatbot sessions.
  - Fields: `chat_session_id`, `sender`, `content`, `created_at`.

### Additional Models
- **AuditLog**:
  - Tracks key actions like login, complaint creation, and status updates.
  - Fields: `action`, `actor_user_id`, `entity_type`, `entity_id`, `metadata`.
- **Notification**:
  - Stores notifications for users.
  - Fields: `user_id`, `title`, `body`, `created_at`.

---

## API Services

### Complaint Service
- **Functions**:
  - `create_manual_complaint`: Handles manual complaint creation.
  - `create_chatbot_complaint`: Creates complaints from chatbot data.
  - `list_user_complaints`: Retrieves complaints for a user.
  - `update_status`: Updates complaint status.

### Chatbot Service
- **Functions**:
  - `start_session`: Initializes a new chatbot session.
  - `get_session_or_404`: Retrieves a session or raises an error.
  - `save_message`: Saves user and bot messages.
  - `submit_final`: Finalizes a session and creates a complaint.

### Notification Service
- **Functions**:
  - `create_notification`: Sends notifications to users.
  - `list_notifications`: Retrieves notifications for a user.

---

## Machine Learning Integration

### ML Models
- **Distress Detection**:
  - Identifies signs of distress or self-harm in user messages.
  - Model: DistilBERT fine-tuned for suicide prevention.
- **Emotion Analysis**:
  - Classifies user emotions (e.g., anger, sadness, fear).
  - Model: DistilBERT fine-tuned for emotion classification.

### ML Pipeline
- **Model Loader**:
  - Loads Hugging Face models from local paths.
- **Inference**:
  - Runs predictions for distress and emotion analysis.
- **Understanding Agent**:
  - Combines ML predictions into a structured understanding of user intent and emotional state.

---

## Machine Learning Decision-Making and Chatbot Interaction

### Overview
The machine learning (ML) components in TrustLine play a critical role in analyzing user messages, detecting distress, and guiding the chatbot's decision-making process. These components ensure that the chatbot provides empathetic and context-aware responses while collecting structured data for complaints.

### ML Components
1. **Distress Detection Model**:
   - Identifies signs of distress or self-harm in user messages.
   - Outputs a label (e.g., "non-suicide", "suicide") and a confidence score.

2. **Emotion Analysis Model**:
   - Classifies user emotions such as anger, sadness, fear, or neutral.
   - Outputs an emotion label and a confidence score.

3. **Understanding Agent**:
   - Combines predictions from the distress and emotion models.
   - Analyzes user intent (e.g., complaint filing, general support, or crisis).
   - Generates a structured summary of the user's state, including:
     - Detected emotion and distress levels.
     - Intent classification (e.g., "complaint", "cybercrime", "self-harm").
     - Suicide risk assessment.

### Interaction with the Chatbot
The chatbot engine, known as the Mithuru Engine, integrates ML predictions to adapt its responses dynamically. The interaction flow is as follows:

1. **Message Processing**:
   - The chatbot receives a user message and sends it to the ML pipeline.
   - The Understanding Agent processes the message and returns a structured understanding.

2. **Decision-Making**:
   - Based on the ML output, the chatbot determines the appropriate mode:
     - **Support Mode**: General listening and trust-building.
     - **Guided Intake Mode**: Step-by-step complaint filing.
     - **Vulnerable Support Mode**: Gentle intake for distressed users.
     - **Hard Crisis Mode**: Crisis intervention for self-harm risks.
     - **Post Complaint Mode**: Emotional support after complaint submission.

3. **Response Generation**:
   - The chatbot uses the structured understanding to craft a response.
   - Responses are filtered for safety and compliance with guidelines.

4. **Field Extraction**:
   - The ML pipeline extracts structured data (e.g., victim details, incident dates) from user messages.
   - Extracted fields are added to the complaint draft.

5. **Complaint Submission**:
   - Once all required fields are collected, the chatbot finalizes the complaint and provides a tracking ID.

### Example Workflow
1. **User Message**: "I feel scared because someone leaked my private photos online."
2. **ML Analysis**:
   - Distress Detection: Label = "non-suicide", Confidence = 0.85.
   - Emotion Analysis: Label = "fear", Confidence = 0.92.
   - Intent: "complaint".
3. **Chatbot Decision**:
   - Mode: Guided Intake.
   - Response: "I'm so sorry to hear that. Let's work together to file a complaint and address this issue. Can you tell me more about the platform where the photos were leaked?"
4. **Field Extraction**:
   - Extracted Field: `source_platform = "online"`.
5. **Complaint Submission**:
   - After collecting all fields, the chatbot submits the complaint and provides a tracking ID.

### Safety and Compliance
- The chatbot ensures that all responses are filtered for safety and adhere to ethical guidelines.
- In cases of high distress or crisis, the chatbot provides hotline information and encourages the user to seek immediate help.

### Future Enhancements
- **Multilingual Support**: Fine-tune models for local languages.
- **Sentiment Analysis**: Enhance user understanding with sentiment detection.
- **Real-Time Adaptation**: Improve response generation with real-time feedback loops.

---

## Chatbot Workflow

### Conversation Flow
1. **Session Initialization**:
   - Starts a new session and loads previous messages.
2. **Message Processing**:
   - Analyzes user messages for distress, emotion, and intent.
   - Classifies incidents and extracts structured data.
3. **Guided Intake**:
   - Collects complaint details step-by-step.
4. **Complaint Submission**:
   - Finalizes the complaint and provides a tracking ID.

### Modes
- **Support**: Initial listening and trust-building.
- **Guided Intake**: Step-by-step complaint filing.
- **Vulnerable Support**: Gentle intake for distressed users.
- **Hard Crisis**: Crisis intervention for self-harm risks.
- **Post Complaint**: Emotional support after complaint submission.

---

## Deployment Notes

### Backend
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string.
  - `SECRET_KEY`: JWT secret key.
  - `SUICIDE_MODEL_PATH`: Path to distress detection model.
  - `EMOTION_MODEL_PATH`: Path to emotion analysis model.
- **Startup**:
  - Run `uvicorn app.main:app --reload` to start the server.

### Frontend
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: Base URL for backend API.
- **Startup**:
  - Run `npm run dev` to start the development server.

---

## Future Enhancements
- **Scalability**:
  - Migrate to cloud-based storage for evidence uploads.
  - Implement horizontal scaling for high traffic.
- **AI Improvements**:
  - Fine-tune ML models for local languages.
  - Add sentiment analysis for better user understanding.
- **User Experience**:
  - Add real-time notifications.
  - Enhance chatbot responses with multilingual support.

---

## Contributors
- **Backend Development**: [Your Name]
- **Frontend Development**: [Your Name]
- **ML Integration**: [Your Name]

---

## License
This project is licensed under the MIT License.