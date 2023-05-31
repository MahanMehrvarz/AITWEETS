# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 09:57:02 2022

@author: mmehrvarz
"""



from creds import *
import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

import pandas as pd
import pprint as pp
from tweepy import OAuth1UserHandler, API
import openai
from txToImg import *
import datetime
import schedule, time


# Our Host URL should not be prepended with "https" nor should it have a trailing slash.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

# Sign up for an account at the following link to get an API Key.
# https://beta.dreamstudio.ai/membership

# Click on the following link once you have created an account to be taken to your API Key.
# https://beta.dreamstudio.ai/membership?tab=apiKeys

# Paste your API Key below.

os.environ['STABILITY_KEY'] = STABILITYKEY

# Set up our connection to the API.
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-v1-5", # Set the engine to use for generation. 
    # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0 
    # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
)

def imgGen(prmpt,name):
    # Set up our initial generation parameters.
    answers = stability_api.generate(
        prompt=prmpt,
        seed=992446758, # If a seed is provided, the resulting generated image will be deterministic.
                        # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
                        # Note: This isn't quite the case for Clip Guided generations, which we'll tackle in a future example notebook.
        steps=70, # Amount of inference steps performed on image generation. Defaults to 30. 
        cfg_scale=9.0, # Influences how strongly your generation is guided to match your prompt.
                       # Setting this value higher increases the strength in which it tries to match your prompt.
                       # Defaults to 7.0 if not specified.
        width=640, # Generation width, defaults to 512 if not included.
        height=384, # Generation height, defaults to 512 if not included.
        samples=1, # Number of images to generate, defaults to 1 if not included.
        sampler=generation.SAMPLER_K_DPMPP_2M # Choose which sampler we want to denoise our generation with.
                                                     # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                     # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
    )
    
    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated images.
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(name+ ".png") # Save our generated images with their seed number as the filename.

def gptgen(prompt):
    openai.api_key = OPENAIKEY

    response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    temperature=0.6,
    max_tokens=270,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].text

teststring="This question already has answers here:How to properly ignore exceptions (12 answers)Closed 6 years ago.I am using a Python script for executing some function in Abaqus. Now, after running for some iterations Abaqus is exiting the script due to an error.Is it possible in Python to bypass the error and continue with the other iterations?The error message is This question already has answers here:How to properly ignore exceptions (12 answers)Closed 6 years ago.I am using a Python script for executing some function in Abaqus. Now, after running for some iterations Abaqus is exiting the script due to an error.Is it possible in Python to bypass the error and continue with the other iterations?The error message is"

def tweeter(hashtag):
    error=False
    while error==False:
        error=True
        print("hi")
        #we get the now to name the image file
        now = datetime.datetime.now()
             
        #this is tweepy fundamentals to search for a hashtag
        auth = OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        api = API(auth)
        KEYWORDS = hashtag  
        QUERY = hashtag+" -filter:retweets"
        tweets = api.search_tweets(QUERY, tweet_mode="extended", result_type="recent" ,lang="en")
        
        #emty tweet string container
        mystr=""
        
        
        for i in tweets:
            #all tweets texts merged into the container
            mystr+=i.full_text
        
        #creating a summary of all tweets with GPT3 of Open AI
        summary=gptgen("summarize these tweet into a paragraph:"+"\n"+mystr)
    
        # print ("summary is: "+summary)
        
        #asking GPT3 to write a tweet based on a summary it wrote in the previous step
        #we first need to make the prompt and then pass the prompt to GPT3
        cmdForPmptTxt="write a short tweet about this text: "+ summary
        #passing the prompt and creating the tweet
        tweet=gptgen(cmdForPmptTxt)
        #now we need to create a prompt for stable stability AI (davinchi) to create an Image for the tweet
        #asking GPT3 to write a prompt based on the tweet so that we can pass it to davinchi 
        cmdForImgPmpt="describe a hyperealistic digital painting with nice use of color and light about this:"+ tweet
        #Passing the command to GPT3 in order to receive the text to Image prompt (i know it's confusing)
        prompt=gptgen(cmdForImgPmpt)
        
        # print("------------------2")
        # print ("prompt is: "+prompt)
        # print("------------------3")
        # print("command for img: "+cmdForImgPmpt)
        # print("tweet is: "+tweet)
    
        #naming the image that davinchi created to store it
        name=str(now).replace(" " ,"").replace(":","").replace(".","")
        #here gicing the Davinchi model the prompt and the file name and it generates an Image
        img=imgGen(prompt ,name)
        #tweeting with media

        try:
            api.update_status_with_media(tweet,name+".png")
            error=True
            print("posted")
        except:
            error=False
            print("bye")
            pass


tweeter("#anygivenhashtag")
