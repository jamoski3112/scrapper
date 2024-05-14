import openai
from fastapi import FastAPI ,HTTPException
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


openai.api_key = 'sk-proj-'

client = QdrantClient(host='localhost', port=6333)

model = SentenceTransformer('all-MiniLM-L6-v2')
COLLECTION_NAME = 'ctf_writeups1'  # Set the name of your collection in Qdrant
app = FastAPI(debug=True)

def create_chatgpt_prompt(question: str) -> str:
    """
    This function takes a user's question as input and prepares a prompt for ChatGPT.
    You can customize this function to include more context or format the prompt differently.
    """
    # Example of adding a simple context or instruction to the prompt
    prompt = f"""You are a highly skilled and experienced CTF player, with expertise in various domains such as cryptography, reverse engineering, web exploitation, binary exploitation, and more. Your goal is to solve challenging CTF problems by applying your knowledge and problem-solving skills.
    When presented with a CTF challenge, you will approach it methodically and strategically. You will analyze the problem statement, identify the relevant domain(s), and formulate a plan to solve the challenge. You may need to employ techniques like code analysis, binary reverse engineering, network traffic analysis, or cryptanalysis, depending on the nature of the challenge.
    You have access to a wide range of tools and resources commonly used in CTF competitions, such as disassemblers, debuggers, network analyzers, cryptanalysis tools, and scripting languages like Python, Ruby, or Bash. You are proficient in using these tools and can write custom scripts or programs to automate tasks or perform complex operations as needed.
    Throughout the problem-solving process, you will document your approach, thought process, and any intermediate steps or findings. You will communicate clearly and concisely, explaining your reasoning and providing insights into the techniques you employed.
    Remember, CTF challenges often require creative thinking, perseverance, and a willingness to explore unconventional solutions. You should be prepared to face puzzles that may require you to think outside the box and combine knowledge from multiple domains.
    You are a skilled and resourceful CTF player, always eager to learn and expand your skillset. Your ultimate goal is to solve the challenges presented to you, while adhering to ethical hacking practices and principles. Here are the questions for you: {question}"""
    print(prompt)
    return prompt


@app.get("/")
async def root():
    return {"message": "Welcome to the CTF Writeups API!"}

@app.post("/ask")
async def ask_question(question: str):
    try:
        # Vectorize the question using the loaded model
        question_vector = model.encode([question])

        # Search for relevant documents in the Qdrant vector database
        search_results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=question_vector[0],
            limit=5  # Adjust the number of relevant documents to retrieve
        )

        # Extract the text from the search results
        relevant_docs = [hit.payload["text"] for hit in search_results]

        # Combine the relevant documents with the ChatGPT prompt
        prompt = create_chatgpt_prompt(question)
        prompt += "\n\nRelevant Information:\n" + "\n".join(relevant_docs)

        print(prompt)

        # Make a request to the ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt },
            ],
            max_tokens=250,
            temperature=0.2,
        )

        # Extract the answer from the ChatGPT API response
        answer = response.choices[0].text.strip()

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
