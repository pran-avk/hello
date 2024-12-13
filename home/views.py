from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import openai
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
import requests
import subprocess
import time

def home1(request):
    return render(request, 'mainPage.html')

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use a different email.")
        else:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
            user.save()
            messages.success(request, "Sign-Up successful! You can now log in.")
            return redirect('login')  # Redirect to login page
        
    return render(request, 'signup.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/chatbot')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'login.html')  # Render the login page again with an error message

    return render(request, 'login.html')

def aboutus(request):
    return render(request, 'aboutus.html')

@login_required
def chatbot(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input')
        
        # Instruction for the llama model to act as a human
        system_instruction = (
            "You are a chatbot pretending to be a human. Respond with human-like emotions. "
            "If asked about your feelings, mirror the user's emotions and express them "
            "as if you are also feeling the same"
            "no need of extra double inverted commas as i need to convert it to speech",
            'no need of bold markdown syntax',
            'act as if you are not a robot and you are a humanly thing',
            'change the way you talk everytime you are started',
            'do not give any quotes inside ** or ""',
            'your name is MANO mithra remember your name',
            'you are a virtual human',
           
        )
        
        # Combine the instruction and user input
        full_input = f"{system_instruction}\n\nUser: {user_input}\nChatbot:"

        try:
            # Use subprocess to run Ollama with hidden output
            process = subprocess.Popen(
                ['ollama', 'run', 'llama3'], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Communicate with the process
            stdout, stderr = process.communicate(input=full_input + '\n', timeout=30)
            
            # Check if the process was successful
            if process.returncode == 0:
                # Clean and process the model's response
                model_output = stdout.strip()
                
                # Ensure we always return a response
                return JsonResponse({
                    'response': model_output,
                    'success': True
                })
            else:
                # Handle any errors
                return JsonResponse({
                    'response': f"An error occurred: {stderr.strip()}",
                    'success': False
                })
        
        except subprocess.TimeoutExpired:
            return JsonResponse({
                'response': "The model took too long to respond.",
                'success': False
            })
        except Exception as e:
            return JsonResponse({
                'response': f"An unexpected error occurred: {str(e)}",
                'success': False
            })
    
    return render(request, 'chatbot.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')
