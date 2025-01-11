import streamlit as st

# HTML content for the Sentiment Analysis app
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis</title>
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            text-align: center;
            background: #fff;
            padding: 40px 30px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 25px;
            color: #333;
        }
        textarea {
            display: block;
            width: 100%;
            height: 150px;
            margin: 15px 0 25px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 16px;
            resize: none;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        textarea:focus {
            border-color: #2575fc;
            outline: none;
        }
        button {
            background-color: #2575fc;
            color: #fff;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background 0.3s ease;
        }
        button:hover {
            background-color: #6a11cb;
        }
        .result {
            margin-top: 30px;
            padding: 15px;
            border-radius: 6px;
            background: #f7f9fc;
            color: #333;
            font-size: 18px;
            font-weight: 500;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            text-align: left;
            white-space: pre-wrap;
            height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sentiment Analysis</h1>
        <textarea id="inputText" placeholder="Enter your tweets (Note: no less than 10)"></textarea>
        <button onclick="analyzeSentiment()">Analyze</button>
        <div class="result" id="result">Your sentiment analysis result will appear here.</div>
    </div>

    <script>
        function analyzeSentiment() {
            // This function will trigger a Streamlit Python function
            const inputText = document.getElementById('inputText').value;
            streamlitApi.setComponentValue(inputText);
        }
    </script>
</body>
</html>
"""

# Function to display HTML content
st.markdown(html_content, unsafe_allow_html=True)

# Placeholder for the sentiment analysis result
result_placeholder = st.empty()

# Function to handle input and display the result
def analyze_sentiment(text):
    # Placeholder for actual sentiment analysis logic
    result = f"Analyzed sentiment for input: {text}"
    return result

# Use Streamlit's input method to capture the textarea content
input_text = st.text_area("Input your text here", height=150, max_chars=None, key="input_text")

if st.button("Analyze"):
    result = analyze_sentiment(input_text)
    result_placeholder.markdown(f"**Result:** {result}", unsafe_allow_html=True)
