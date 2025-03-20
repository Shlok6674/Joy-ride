from django.shortcuts import render, redirect, get_object_or_404
from.models import *
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from.models import User
from django.http import JsonResponse,HttpResponse
from.models import Car,Rental
from.models import Review
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import datetime

# Create your views here.

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        try:
         user = User.objects.get(email=request.POST['email'])
         msg = "Email already exists!!"
         return render(request, 'signup.html', {'msg': msg})
        except User.DoesNotExist:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    name=request.POST['name'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    password=request.POST['password'],
                    profile=request.FILES['profile'],
                    usertype=request.POST['usertype']
                )
                msg = "Signup Successfully!!"
                return render(request, 'login.html', {'msg': msg})
            else:
                msg = "Password & confirm password do not match!!"
                return render(request, 'signup.html', {'msg': msg})
    else:
        return render(request, 'signup.html')

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['profile'] = user.profile.url
                if user.usertype == "customer":
                    return redirect('index')
                else:
                    return redirect('lindex')
            else:
                msg = "Invalid Password!!"
                return render(request, 'login.html', {'msg': msg})
        except User.DoesNotExist:
            msg = "Invalid Email!!"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')

def logout(request):
    request.session.pop('email', None)  # Remove 'email' if it exists
    request.session.pop('profile', None)  # Remove 'profile' if it exists
    return redirect('login')

def cpass(request):
    if request.method=="POST":
        user = User.objects.get(email=request.session['email'])

        if user.password == request.POST['opassword']:
            if request.POST['npassword']==request.POST['cnpassword']:
                user.password = request.POST['npassword']
                user.save()

                return redirect('logout')


            else:
                msg = "New password & confirm new password does not match!!"
                return render(request,'cpass.html',{'msg':msg})

        else:
            msg = "Old password does not match!!"
            return render(request,'cpass.html',{'msg':msg})
        



    else:
        return render(request,'cpass.html')
    

    
def fpass(request):
    if request.method=="POST":
        try:
            email = request.POST.get('email')
            user = User.objects.get(email=email)
            otp = random.randint(1000,9999)
            subject = "Password Reset OTP"
            message = f"your OTP is {otp}"
            email_from = settings.EMAIL_HOST_USER
            receipent_list = [user.email]
            send_mail(subject,message,email_from,receipent_list)
            request.session['email'] = user.email
            request.session['otp'] = otp
            return render(request,'otp.html')
        except User.DoesNotExist: 
            msg="Invalid email id"
            return render(request,'fpass.html',{'msg':msg})
        
    return render(request,'fpass.html')

def otp(request):
    if request.method=="POST":
        try:
           otp = int(request.session.get('otp', 0)) 
           uotp = int(request.POST.get('uotp', 0)) 
           if otp == uotp:
                del request.session['otp']
                return render(request,'newpass.html')
           else:
                msg="Invalid OTP"
                return render(request,'otp.html',{'msg':msg})
        except(ValueError,TypeError):
            msg="An error occured.Please try again."
            return render(request,'otp.html',{'msg':msg})
    return render(request,'otp.html')


def newpass(request):
    if request.method=="POST":
        try:
            email = request.session['email']
            user = User.objects.get(email=email)
            npassword = request.POST['npassword']
            cnpassword = request.POST['cnpassword']
            if npassword == cnpassword:
               user.password = make_password(npassword)
               user.save()
               del request.session['email']
               return redirect('login')
            
            else:
                msg="Password and confirm password do not match"
                return render(request,'newpass.html',{'msg':msg})
        except User.DoesNotExist:
            msg="User not found.Please try again."
            return render(request,'newpass.html',{'msg':msg})
        
    return render(request,'newpass.html')

def uprofile(request):
    try:
        user = User.objects.get(email=request.session['email'])
    except User.DoesNotExist:
        return redirect('login')  # Redirect if user not found (session expired, etc.)

    if request.method == "POST":
        user.name = request.POST.get('name', user.name)  # Use `.get()` to avoid KeyError
        user.mobile = request.POST.get('mobile', user.mobile)

        # Save the user details first
        user.save()

        # Handle profile picture update safely
        if 'profile' in request.FILES:
            user.profile = request.FILES['profile']
            user.save()
            request.session['profile'] = user.profile.url  # Update session with new image

        return redirect('index')  # Redirect to home after updating profile

    return render(request, 'uprofile.html', {'user': user})

def carsingle(request):
    return render(request, 'car/carsingle.html')
       

def about(request):
    return render(request, 'about.html')

def details(request, pk):
    try:
        lessor = User.objects.get(email=request.session['email'])
        car = Car.objects.get(pk=pk)
        related_cars = Car.objects.exclude(pk=pk)[:3]
        related_reviews = Review.objects.filter(car=car)
        print(related_cars)
        print(related_reviews)
        
        if request.method=="POST":
            lessor=User.objects.get(email=request.session['email'])
            car=Car.objects.get(pk=pk)
            review = request.POST['review']
            rating = request.POST['rating']
            Review.objects.create(
                user = lessor,
                car = car,
                review = review,
                rating = rating,
            )
            return redirect('details',pk=pk)
        else:
            return render(request,'details.html',{'car':car,'lessor':lessor,'related_cars':related_cars})
        
    except Exception as e:
        msg = "Please login first !"
        return render(request, 'login.html', {'msg': msg})
    
    # Get reviews for this specific car
    
    

def blog(request):
    return render(request, 'blog.html')

def blogsingle(request):
    return render(request, 'blogsingle.html')


def car(request):
    email = request.session.get('email')  # Retrieve email from session

    if not email:  # If email is not found in the session, redirect to login
        return redirect('login')  # Replace 'login' with your actual login route name

        try:
            user = User.objects.get(email=email)  # Try to fetch the user
        except User.DoesNotExist:
            return redirect('login')  # Redirect to login page if the user doesn't exist

    car = Car.objects.all()  # Fetch all car objects
    return render(request, 'car.html', {'car': car}) 

def details(request,pk):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.get(pk=pk)
    return render(request,'details.html',{'car':car})

def pricing(request):
    return render(request, 'pricing.html')

def services(request):
    return render(request, 'services.html')

def lindex(request):
    return render(request, 'lindex.html')

def add(request):
    if request.method == "POST":
        lessor = User.objects.get(email=request.session['email'])  # ✅ Correct variable name
        try:
            Car.objects.create(
                lessor=lessor,  # ✅ Correct field name
                stransmission=request.POST['stransmission'],
                sfuel=request.POST['sfuel'],
                cname=request.POST['cname'],
                milegae=request.POST['milegae'],
                seats=request.POST['seats'],
                
                luggage=request.POST['luggage'],
                desc=request.POST['desc'],
                cprice=request.POST['cprice'],
                cimage=request.FILES['cimage']
            )
            msg = "Car Added Successfully!!"
            return redirect('view')
        except Exception as e:
            print("**********************", e)
            return redirect('lindex')
    else:
        return render(request, 'add.html')


def view(request):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.filter(lessor=lessor)
   
    return render(request, 'view.html', {'car': car})

def details(request, pk):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.filter(lessor=lessor)
    
    car = Car.objects.get(pk=pk)
    return render(request, 'details.html', {'car': car})

def update(request, pk):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.filter(lessor=lessor)
    
    car = Car.objects.get(pk=pk)
    if request.method == "POST":
        car.cname = request.POST['cname']
        car.cprice = request.POST['cprice']
        car.stransmission = request.POST['stransmission']
        car.sfuel = request.POST['sfuel']
        car.desc = request.POST['desc']
        car.milegae = request.POST['milegae']
        car.luggage = request.POST['luggage']
        car.seats = request.POST['seats']
        
        car.save()
        try:
            car.cimage = request.FILES['cimage']
            car.save()
        except:
            pass
        return redirect('view')
    else:
        return render(request, 'update.html', {'car': car})
    
def l_about(request):
    return render(request, 'l_about.html')

def delete(request,pk):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.get(pk=pk)
    car.delete()
    return redirect('view')

def order_form(request):
    car_id = request.GET.get('car_id')
    car_name = request.GET.get('car_name')
    price = request.GET.get('price')

    # Validate car_id
    try:
        car = Car.objects.get(id=car_id)
        if not car.availability:
            messages.error(request, "This car is no longer available for booking.")
            return redirect('car_list')
    except Car.DoesNotExist:
        messages.error(request, "Invalid car selected.")
        return redirect('car_list')

    # Validate price
    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid price for the selected car.")
        return redirect('car_list')

    # Validate car_name (optional, since it's just for display)
    if not car_name:
        car_name = car.cname  # Fallback to the car's actual name

    return render(request, 'order_form.html', {
        'car_id': car_id,
        'car_name': car_name,
        'price': price
    })

@login_required
def rent_car(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        pickup_place = request.POST.get('pickup_place')
        dropoff_place = request.POST.get('dropoff_place')
        pickup_time = request.POST.get('pickup_time')
        dropoff_time = request.POST.get('dropoff_time')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        total_price = request.POST.get('total_price').replace('$', '')

        # Validate car
        try:
            car = Car.objects.get(id=car_id)
            if not car.availability:
                messages.error(request, "This car is no longer available for booking.")
                return redirect('car_list')
        except Car.DoesNotExist:
            messages.error(request, "Invalid car selected.")
            return redirect('car_list')

        # Validate places
        if not pickup_place or not dropoff_place:
            messages.error(request, "Please provide both pick-up and drop-off places.")
            return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)

        # Validate dates
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            if start_date < datetime.date.today():
                messages.error(request, "Start date cannot be in the past.")
                return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)
            if end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
                return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)

        # Validate times
        try:
            pickup_time = datetime.datetime.strptime(pickup_time, '%H:%M').time()
            dropoff_time = datetime.datetime.strptime(dropoff_time, '%H:%M').time()
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)

        # Validate total price
        try:
            total_price = float(total_price)
            if total_price <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid total price.")
            return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)

        # Create the rental
        try:
            Rental.objects.create(
                user=request.user,
                car=car,
                pickup_place=pickup_place,
                dropoff_place=dropoff_place,
                pickup_time=pickup_time,
                dropoff_time=dropoff_time,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price
            )
            car.availability = False
            car.save()
            messages.success(request, f"Successfully booked {car.cname}! Enjoy your ride.")
            return redirect('car_list')
        except ValidationError as e:
            messages.error(request, f"Error creating rental: {str(e)}")
            return redirect('order_form', car_id=car_id, car_name=car.cname, price=car.cprice)

    return redirect('car_list')