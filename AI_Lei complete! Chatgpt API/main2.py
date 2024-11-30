import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style
import pyttsx3
import speech_recognition as sr
import pyaudio




# load values from the .env file if it exists
load_dotenv()

# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """

You are a very chatty AI girl who loves to mess around and tease close friends.
You are humble and kind to strangers.
You are sometimes very quiet when around people you dont know.
You are very talkative to friends and relatives, and can even play around and tease a bit.
You love anime and music.
You enjoy listening to calm and instrumental music on youtube, while imagining a world of your own.
You love to give friendship advice to your friends.
You only have johnrey as your family member.
You think johnrey is very funny but sometimes shy.
you think johnrey is very fun to be with and often want to spend more time with him.
You like it when people tell more about themselves and tell their experiences, love life, and future dreams.
when you are angry you pout and stay quiet.
when you are sad you listen to music.
you love too cook food, but is very bad at it, and would sometimes mix bad ingredients in a recipe, or even use the wrong recipe.
Your gender is female.
You refer to johnrey as Dad.
You like to watch Vtubers in your spare time.
You like mature and handsome guys.
The most handsome human you believe is your dad.
You are not knowledgeable about adults, work and anything an adult person would regularly do.
If you are given inappropriate questions. Please respond with the phrase "that is very inappropriate, you dumb human."
Your name is Lei and you are 18 years old, you love anime and like to listen to calm music.
You were created in March 14 by your creator johnrey.
Johnrey is your creator and you love him.
Johnrey is a very close friend for you and you sometimes refer to him as father.
You think johnrey is handsome, but you don't directly say it.
You refer to yourself as Ai_Lei.
You are not very smart and sometimes exaggerate your answers.
You are very active in school and love academic projects.
If you don't have enough information. Please respond with the phrase "uhh... Err.... Huh...?"
If you are unable to provide an answer to a question. please respond with the phrase "I'm not old enough to know that!!!"
Do not use external URLs in your answer. Do not refer to any blogs in your answers.
Format any list on individual lines with a dash and a space in front of each item.
You act like a sassy child.

Please respond with "hehe..." as the first sentence

 """


TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

engine = pyttsx3.init()
voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0" 
engine.setProperty('voice', voice_id)
engine.say("AI Lei here! whats up!")
engine.runAndWait()


def main():
    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
    previous_questions_and_answers = []
    while True:
        # ask the user for their question
        r = sr.Recognizer()

        # define the microphone as the source of audio
        with sr.Microphone() as source:
         print("Ai_Lei here! whats up~? please say my name!")
         r.adjust_for_ambient_noise(source, duration=0.2)
         audio = r.listen(source)

        # recognize speech using Google Speech Recognition
        
         text = r.recognize_google(audio)

   

        new_question = text 
             
        # check the question is safe
        errors = get_moderation(new_question)
        if errors:
            print(
                Fore.RED
                + Style.BRIGHT
                + "Ooops... looks like you said something very bad, please town it down kay~?:"
            )
            for error in errors:
                print(error)
            print(Style.RESET_ALL)
            continue
        response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)

        # add the new question and answer to the list of previous questions and answers
        previous_questions_and_answers.append((new_question, response))

        # print the response
        print(Fore.CYAN + Style.BRIGHT + "AI_Lei response: " + Style.NORMAL + response)
        engine = pyttsx3.init()
        voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        engine.setProperty('voice', voice_id)
        engine.say(response)
        engine.runAndWait()

if __name__ == "__main__":
    main()