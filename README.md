# TalentScout - AI Hiring Assistant

A Streamlit-based chatbot application designed to streamline the technical screening process for hiring candidates. TalentScout collects candidate information and generates personalized technical questions based on the candidate's declared tech stack.

## Features

- 🤖 Interactive chatbot interface with Streamlit
- 📋 Comprehensive candidate data collection
- 🔧 AI-powered technical question generation using OpenAI
- 💬 Conversation context management
- 🚪 Graceful exit handling
- 🎯 Modular and extensible architecture

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### OpenAI API Key

To use the AI question generation feature, you need an OpenAI API key:

1. Sign up for an OpenAI account at [https://openai.com](https://openai.com)
2. Navigate to the API keys section in your dashboard
3. Create a new API key
4. Add it to your `.env` file

## Usage

1. **Greeting Phase**: The chatbot introduces itself and explains its purpose
2. **Data Collection**: Candidate fills out a form with personal and professional information
3. **Technical Assessment**: AI generates 3-5 questions per technology in the candidate's tech stack
4. **Completion**: Summary of collected information and thank you message

### Exit Commands

Type any of the following to exit the conversation:
- "exit"
- "quit" 
- "bye"
- "goodbye"
- "stop"

## Architecture

The application follows a modular design:

- `Config`: Application configuration and constants
- `ConversationManager`: Manages conversation state and history
- `CandidateDataCollector`: Handles candidate information collection and validation
- `TechQuestionGenerator`: Generates technical questions using OpenAI API
- `TalentScoutApp`: Main application class coordinating all components

## Extensibility

The application is designed for easy extension:

### Adding New Features

1. **Sentiment Analysis**: Integrate with sentiment analysis APIs
2. **Multilingual Support**: Add translation capabilities
3. **Database Integration**: Store candidate responses in a database
4. **Email Notifications**: Send confirmation emails to candidates
5. **Advanced Analytics**: Add dashboards for hiring metrics

### Modifying Question Generation

Edit the `TechQuestionGenerator` class to:
- Use different AI models
- Customize question templates
- Add domain-specific question banks
- Implement different difficulty levels

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Ensure your API key is valid and has sufficient credits
2. **Streamlit Connection Issues**: Check your network connection and firewall settings
3. **Form Validation Errors**: Make sure all required fields are filled correctly

### Getting Help

If you encounter issues:

1. Check the browser console for error messages
2. Verify your OpenAI API key is correctly set
3. Ensure all dependencies are installed correctly

## License

This project is open source and available under the MIT License.