import streamlit as st
import openai
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration and Constants
class Config:
    """Configuration class for the TalentScout application"""
    APP_TITLE = "TalentScout - AI Hiring Assistant"
    GREETING_MESSAGE = """
    👋 Welcome to TalentScout! 
    
    I'm your AI-powered hiring assistant here to help you through the technical screening process. 
    I'll collect some basic information about you and then assess your technical skills through 
    relevant questions based on your tech stack.
    
    Let's get started! 😊
    """
    EXIT_KEYWORDS = ["exit", "quit", "bye", "goodbye", "stop"]
    THANK_YOU_MESSAGE = """
    Thank you for your time! Your responses have been recorded. 
    Our hiring team will review your information and get back to you soon. 
    
    Good luck! 🚀
    """

class ConversationManager:
    """Manages conversation state and context"""
    
    def __init__(self):
        self.state = st.session_state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize all session state variables"""
        if 'conversation_history' not in self.state:
            self.state.conversation_history = []
        if 'candidate_data' not in self.state:
            self.state.candidate_data = {}
        if 'current_stage' not in self.state:
            self.state.current_stage = 'greeting'
        if 'tech_questions' not in self.state:
            self.state.tech_questions = {}
        if 'current_tech_index' not in self.state:
            self.state.current_tech_index = 0
        if 'tech_stack_list' not in self.state:
            self.state.tech_stack_list = []
    
    def add_to_history(self, role: str, message: str):
        """Add message to conversation history"""
        self.state.conversation_history.append({
            'role': role,
            'message': message,
            'timestamp': datetime.now()
        })
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation context for LLM"""
        context = ""
        for entry in self.state.conversation_history[-10:]:  # Last 10 messages
            context += f"{entry['role'].upper()}: {entry['message']}\n"
        return context

class CandidateDataCollector:
    """Handles collection and validation of candidate information"""
    
    REQUIRED_FIELDS = [
        'full_name', 'email', 'phone_number', 'years_experience',
        'desired_positions', 'current_location', 'tech_stack'
    ]
    
    def __init__(self):
        self.state = st.session_state
    
    def collect_basic_info(self):
        """Collect basic candidate information using Streamlit forms"""
        st.header("📋 Candidate Information")
        
        with st.form("candidate_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name *", placeholder="John Doe")
                email = st.text_input("Email Address *", placeholder="john.doe@email.com")
                phone_number = st.text_input("Phone Number *", placeholder="+1 (555) 123-4567")
                years_experience = st.number_input("Years of Experience *", min_value=0, max_value=50, value=0)
            
            with col2:
                desired_positions = st.multiselect(
                    "Desired Position(s) *",
                    ["Software Engineer", "Data Scientist", "Frontend Developer", "Backend Developer", 
                     "Full Stack Developer", "DevOps Engineer", "Machine Learning Engineer", "QA Engineer"]
                )
                current_location = st.text_input("Current Location *", placeholder="San Francisco, CA")
                tech_stack = st.text_area(
                    "Tech Stack (comma-separated) *", 
                    placeholder="Python, JavaScript, React, Node.js, PostgreSQL, AWS"
                )
            
            submitted = st.form_submit_button("Submit Information")
            
            if submitted:
                if self._validate_form(full_name, email, phone_number, years_experience, 
                                    desired_positions, current_location, tech_stack):
                    self._save_candidate_data({
                        'full_name': full_name,
                        'email': email,
                        'phone_number': phone_number,
                        'years_experience': years_experience,
                        'desired_positions': desired_positions,
                        'current_location': current_location,
                        'tech_stack': tech_stack
                    })
                    return True
                else:
                    st.error("Please fill in all required fields correctly.")
        return False
    
    def _validate_form(self, full_name, email, phone_number, years_experience, 
                      desired_positions, current_location, tech_stack) -> bool:
        """Validate form inputs"""
        if not all([full_name, email, phone_number, current_location, tech_stack]):
            return False
        if not desired_positions:
            return False
        if not self._validate_email(email):
            st.error("Please enter a valid email address.")
            return False
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _save_candidate_data(self, data: Dict[str, Any]):
        """Save candidate data to session state"""
        self.state.candidate_data = data
        # Parse tech stack into list
        tech_list = [tech.strip() for tech in data['tech_stack'].split(',') if tech.strip()]
        self.state.tech_stack_list = tech_list

class TechQuestionGenerator:
    """Generates technical questions using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Try to get API key from multiple sources
        self.api_key = api_key
        if not self.api_key:
            try:
                self.api_key = st.secrets.get("OPENAI_API_KEY", "")
            except:
                self.api_key = ""
        
        # Try environment variable as fallback
        if not self.api_key:
            import os
            self.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_questions_for_tech(self, technology: str, experience_level: int) -> List[str]:
        """Generate technical questions for a specific technology"""
        if not self.api_key:
            return self._get_fallback_questions(technology)
        
        try:
            prompt = f"""
            Generate 3-5 technical interview questions for {technology} suitable for a candidate 
            with approximately {experience_level} years of experience. 
            
            The questions should:
            1. Assess practical knowledge and problem-solving skills
            2. Be appropriate for the experience level
            3. Cover different aspects of the technology (fundamentals, advanced concepts, best practices)
            4. Be clear and concise
            
            Return only the questions as a JSON array of strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical hiring expert. Generate relevant technical interview questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            questions_text = response.choices[0].message.content.strip()
            # Try to parse as JSON, fallback to splitting by newlines
            try:
                questions = json.loads(questions_text)
            except json.JSONDecodeError:
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            return questions[:5]  # Return max 5 questions
            
        except Exception as e:
            st.warning(f"Could not generate questions using OpenAI: {e}")
            return self._get_fallback_questions(technology)
    
    def _get_fallback_questions(self, technology: str) -> List[str]:
        """Fallback questions if API is unavailable"""
        fallback_questions = {
            'python': [
                "What are the key differences between lists and tuples in Python?",
                "How does Python handle memory management?",
                "Explain the concept of decorators in Python.",
                "What are some common use cases for generators?"
            ],
            'javascript': [
                "Explain the event loop in JavaScript.",
                "What are the differences between let, const, and var?",
                "How does prototypal inheritance work in JavaScript?",
                "What are promises and how do they work?"
            ],
            'react': [
                "What is the virtual DOM and how does it work?",
                "Explain the component lifecycle methods.",
                "What are hooks and how do they differ from class components?",
                "How would you optimize React application performance?"
            ],
            'node.js': [
                "How does Node.js handle asynchronous operations?",
                "Explain the event-driven architecture of Node.js.",
                "What are streams and how are they used?",
                "How would you handle memory leaks in Node.js?"
            ]
        }
        
        tech_lower = technology.lower()
        for key, questions in fallback_questions.items():
            if key in tech_lower:
                return questions
        
        return [
            f"What experience do you have with {technology}?",
            f"Describe a challenging project you built using {technology}.",
            f"What are the best practices for working with {technology}?",
            f"How would you troubleshoot performance issues in {technology}?"
        ]

class TalentScoutApp:
    """Main application class for TalentScout"""
    
    def __init__(self):
        self.config = Config()
        self.conversation_manager = ConversationManager()
        self.data_collector = CandidateDataCollector()
        self.question_generator = TechQuestionGenerator()
        
        # Setup page configuration
        st.set_page_config(
            page_title=self.config.APP_TITLE,
            page_icon="🤖",
            layout="wide"
        )
    
    def run(self):
        """Main application loop"""
        st.title("🤖 TalentScout - AI Hiring Assistant")
        
        # Check for exit commands
        if self._check_exit_command():
            return
        
        # Main application flow
        if self.conversation_manager.state.current_stage == 'greeting':
            self._show_greeting()
        elif self.conversation_manager.state.current_stage == 'data_collection':
            self._collect_candidate_data()
        elif self.conversation_manager.state.current_stage == 'technical_assessment':
            self._conduct_technical_assessment()
        elif self.conversation_manager.state.current_stage == 'completion':
            self._show_completion()
    
    def _show_greeting(self):
        """Display greeting message"""
        st.markdown(self.config.GREETING_MESSAGE)
        if st.button("Let's Begin!"):
            self.conversation_manager.state.current_stage = 'data_collection'
            st.rerun()
    
    def _collect_candidate_data(self):
        """Collect candidate information"""
        if self.data_collector.collect_basic_info():
            self.conversation_manager.state.current_stage = 'technical_assessment'
            self.conversation_manager.add_to_history('system', 'Candidate completed basic information form')
            st.rerun()
    
    def _conduct_technical_assessment(self):
        """Conduct technical assessment based on tech stack"""
        tech_stack = self.conversation_manager.state.tech_stack_list
        
        if not tech_stack:
            st.error("No technologies specified for assessment.")
            return
        
        current_index = self.conversation_manager.state.current_tech_index
        
        if current_index >= len(tech_stack):
            self.conversation_manager.state.current_stage = 'completion'
            st.rerun()
            return
        
        current_tech = tech_stack[current_index]
        
        # Generate questions if not already generated
        if current_tech not in self.conversation_manager.state.tech_questions:
            experience = self.conversation_manager.state.candidate_data.get('years_experience', 0)
            questions = self.question_generator.generate_questions_for_tech(current_tech, experience)
            self.conversation_manager.state.tech_questions[current_tech] = questions
        
        # Display current technology assessment
        st.header(f"🔧 Technical Assessment: {current_tech}")
        st.info(f"Please answer the following questions about {current_tech}")
        
        questions = self.conversation_manager.state.tech_questions[current_tech]
        
        with st.form(f"tech_assessment_{current_tech}"):
            responses = []
            for i, question in enumerate(questions):
                response = st.text_area(
                    f"Q{i+1}: {question}",
                    placeholder="Your answer here...",
                    height=100
                )
                responses.append(response)
            
            submitted = st.form_submit_button("Submit Answers")
            
            if submitted:
                if all(responses):  # Check if all questions are answered
                    # Save responses
                    tech_responses = self.conversation_manager.state.candidate_data.get('tech_responses', {})
                    tech_responses[current_tech] = {
                        'questions': questions,
                        'answers': responses
                    }
                    self.conversation_manager.state.candidate_data['tech_responses'] = tech_responses
                    
                    # Move to next technology
                    self.conversation_manager.state.current_tech_index += 1
                    st.rerun()
                else:
                    st.error("Please answer all questions before submitting.")
    
    def _show_completion(self):
        """Show completion message"""
        st.balloons()
        st.success("🎉 Assessment Complete!")
        st.markdown(self.config.THANK_YOU_MESSAGE)
        
        # Show summary of collected data
        with st.expander("📊 Review Your Information"):
            candidate_data = self.conversation_manager.state.candidate_data
            st.json(candidate_data)
        
        if st.button("Start New Session"):
            # Clear session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    def _check_exit_command(self) -> bool:
        """Check if user wants to exit the conversation"""
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            self.conversation_manager.add_to_history('user', user_input)
            
            # Check for exit keywords
            if any(keyword in user_input.lower() for keyword in self.config.EXIT_KEYWORDS):
                st.info(self.config.THANK_YOU_MESSAGE)
                return True
            
            # Handle unexpected inputs
            st.warning("I'm here to help with your hiring process. Please use the forms above to provide information.")
        
        return False

# Main execution
if __name__ == "__main__":
    app = TalentScoutApp()
    app.run()
