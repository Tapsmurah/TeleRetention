from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.models import User, auth # type: ignore
from django.contrib import messages  # type: ignore
from django.contrib.auth.decorators import login_required  # type: ignore
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth import authenticate, login as auth_login # type: ignore
from django.shortcuts import render # type: ignore
from django.utils import timezone # type: ignore
import pandas as pd # type: ignore
from .model_utils import predict_and_recommend
from .models import ChurnPrediction
import json


@login_required(login_url='login')
def predict_and_recommend_view(request):
    if request.method == 'POST':

        # Extract raw user data from the request
        user_data = {
            'Customer ID': request.POST.get('customer_id', '0'),
            'Age': int(request.POST.get('age', 0)),
            'Senior Citizen': int(request.POST.get('senior_citizen', 0)),
            'Gender': request.POST.get('gender', 'Unknown'),
            'Location': request.POST.get('location', 'Unknown'),
            'Tenure': int(request.POST.get('tenure', 0)),
            'Area code': int(request.POST.get('area_code', '0')),
            'International Plan': int(request.POST.get('international_plan', 0)),  
            'Voice Mail Plan': int(request.POST.get('voice_mail_plan', 0)),  
            'Number vmail messages': int(request.POST.get('number_vmail_messages', 0)),
            'Customer service calls': int(request.POST.get('customer_service_calls', 0)),
            'Total day minutes': float(request.POST.get('total_day_minutes', 0)),
            'Total day calls': int(request.POST.get('total_day_calls', 0)),
            'Total day charge': float(request.POST.get('total_day_charge', 0)),
            'Total eve minutes': float(request.POST.get('total_eve_minutes', 0)),
            'Total eve calls': int(request.POST.get('total_eve_calls', 0)),
            'Total eve charge': float(request.POST.get('total_eve_charge', 0)),
            'Total night minutes': float(request.POST.get('total_night_minutes', 0)),
            'Total night calls': int(request.POST.get('total_night_calls', 0)),
            'Total night charge': float(request.POST.get('total_night_charge', 0)),
            'Total intl minutes': float(request.POST.get('total_intl_minutes', 0)),
            'Total intl calls': int(request.POST.get('total_intl_calls', 0)),
            'Total intl charge': float(request.POST.get('total_intl_charge', 0)),
        }

        # Call the predict_and_recommend function to get churn probability and recommendations
        churn_proba, recommendations = predict_and_recommend(user_data)

        # Generate output messages based on churn probability (using 70% as the threshold)
        if churn_proba > 0.7:
            output1 = '<span style="color: red;">This customer is likely to churn!</span>'
            output2 = 'Confidence: <span style="color: red;">{:.2f}%</span>'.format(churn_proba * 100)
        else:
            output1 = '<span style="color: green;">This customer is likely to continue!</span>'
            output2 = 'Confidence: <span style="color: green;">{:.2f}%</span>'.format(churn_proba * 100)

        # Save the prediction data to the database
        ChurnPrediction.objects.create(
            customer_id=user_data['Customer ID'],
            age=user_data['Age'],
            senior_citizen=user_data['Senior Citizen'],
            gender=user_data['Gender'],
            location=user_data['Location'],
            tenure=user_data['Tenure'],
            total_day_charge=user_data['Total day charge'],
            total_night_charge=user_data['Total night charge'],
            total_eve_charge=user_data['Total eve charge'],
            total_intl_charge=user_data['Total intl charge'],
            prediction_output=output1,
            prediction_details=output2,
            recommendations=json.dumps(recommendations),
            created_at=timezone.now()
        )

        # Pass results to the template
        context = {
            'output1': output1,
            'output2': output2,
            #'churn_proba': churn_proba,
            'recommendations': recommendations,
            'customer_id': user_data['Customer ID'],
            'age': user_data['Age'],
            'senior_citizen': user_data['Senior Citizen'],
            'gender': user_data['Gender'],
            'location': user_data['Location'],
            'tenure': user_data['Tenure'],
            # Service plans
            'international_plan': user_data['International Plan'],
            'voice_mail_plan': user_data['Voice Mail Plan'],
            'number_vmail_messages': user_data['Number vmail messages'],
            'customer_service_calls': user_data['Customer service calls'],
            # Day usage
            'total_day_minutes': user_data['Total day minutes'],
            'total_day_calls': user_data['Total day calls'],
            'total_day_charge': user_data['Total day charge'],
            # Evening usage
            'total_eve_minutes': user_data['Total eve minutes'],
            'total_eve_calls': user_data['Total eve calls'],
            'total_eve_charge': user_data['Total eve charge'],
            # Night usage
            'total_night_minutes': user_data['Total night minutes'],
            'total_night_calls': user_data['Total night calls'],
            'total_night_charge': user_data['Total night charge'],
            # International usage
            'total_intl_minutes': user_data['Total intl minutes'],
            'total_intl_calls': user_data['Total intl calls'],
            'total_intl_charge': user_data['Total intl charge'],
        }

        return render(request, 'main/results.html', context)

        
    # If it's a GET request, render the input form
    return render(request, 'main/retention.html')


@login_required(login_url='login')
def home(request):
    try:
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
    except (User.DoesNotExist, Profile.DoesNotExist):
        # Handle the case where either user or profile doesn't exist
        user_profile = None
    
    return render(request, 'main/index.html', {'user_profile': user_profile})

@login_required(login_url='login')
def results(request):
    return render(request, 'main/results.html')

@login_required(login_url='login')
def churn_rate_and_recommendations(request):
    
    return render(request, 'main/predictionsrecommendations.html')

@login_required(login_url='login')
def summary(request):
    return render(request, 'main/summary.html')

@login_required(login_url='login')
def about(request):
    return render(request, 'main/about.html')

@login_required(login_url='login')
def reason(request):
    return render(request, 'main/reason.html')

@login_required(login_url='login')
def lockscreen_view(request):
    # Get the current date and time
    current_time = timezone.now().strftime("%I:%M:%S %p")
    current_date = timezone.now().strftime("%A, %B %d, %Y")
    
    # Prepare context with current time, date, and any messages
    context = {
        'current_time': current_time,
        'current_date': current_date,
    }

    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            auth_login(request, user)  
            request.session['locked'] = False  
            return redirect('/')  
        else:
            messages.error(request, 'Invalid password. Please try again.')

    return render(request, 'registration/lock.html', context)

@login_required(login_url='login')
def myprofile(request):
    try:
        user_profile = get_object_or_404(Profile, user=request.user)

        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                # Check if a new image was uploaded
                if 'profileimg' in request.FILES:
                    # Delete old image file if it exists and isn't the default
                    if user_profile.profileimg and hasattr(user_profile.profileimg, 'url'):
                        try:
                            if 'default' not in user_profile.profileimg.url:
                                user_profile.profileimg.delete(save=False)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")

                profile = form.save(commit=False)
                profile.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('myprofile')
        else:
            form = ProfileForm(instance=user_profile)

        context = {
            'form': form,
            'user_profile': user_profile,
            'profile_image_url': user_profile.profileimg.url if user_profile.profileimg else None,
        }
        return render(request, 'main/myprofile.html', context)

    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return redirect('home')

def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already taken!....')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken!....')
                return redirect('register')
            elif len(password1) < 4:
                messages.info(request,'Password must be at least 4 characters.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password1)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                #messages.info(request, 'Account successfully created!')
            return redirect('myprofile')
        else:
            messages.info(request, 'Password do not match!...')
            return redirect('register')
        
    else:
        return render(request, 'registration/register.html')
                  
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username exists
        if User.objects.filter(username=username).exists():
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid password! Please try again...')
        else:
            messages.error(request, 'Username not found!...')

        return redirect('login')

    else:
        return render(request, 'registration/login.html')

def passwordrecovery(request):
    return render(request, 'registration/password-recovery.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')