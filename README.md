# Writing Coach: Real-time Feedback on Writing Style, Grammar, and Structure

Writing Coach is a Streamlit-based web application that provides real-time feedback on writing style, grammar, and structure. This interactive tool uses various language models to analyze text and offer constructive criticism and suggestions for improvement across different types of writing.

## Features

- Interactive interface for submitting text and receiving feedback
- Support for multiple AI models, including OpenAI's GPT models and Ollama's local models
- Customizable writing type and feedback focus
- Dark/Light theme toggle
- Writing session saving and loading functionality
- Token usage tracking

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/writing-coach.git
   cd writing-coach
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

4. (Optional) If you want to use Ollama models, make sure you have Ollama installed and running on your system.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run writing_coach.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter your name, select the writing type and feedback focus, and start submitting your text for feedback!

## Customization

- You can modify the `WRITING_TYPES` and `FEEDBACK_CATEGORIES` lists in the code to add or remove types of writing and feedback categories.
- The custom instructions for the AI can be adjusted in the sidebar of the application.

## Contributing

Contributions to improve the Writing Coach are welcome! Please feel free to submit pull requests or open issues to discuss potential enhancements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
