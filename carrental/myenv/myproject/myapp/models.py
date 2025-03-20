from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    email=models.EmailField()
    mobile=models.BigIntegerField()
    password=models.CharField(max_length=20)
    profile = models.ImageField(default="")
    usertype = models.CharField(max_length=20,default="customer")
    
    def __str__(self): #for printing object
        return self.name
    
class Car(models.Model):
    lessor = models.ForeignKey(User,on_delete=models.CASCADE)
    
    transmission = (
        
        ("Manual","Manual"),
        ("Auto","Auto")
    )
    fuel = (

        ("CNG","CNG"),
        ("Petrol","Petrol"),
        ("Diesel","Diesel")
    )
    sfuel = models.CharField(max_length=50,choices=fuel)
    stransmission = models.CharField(choices=transmission,max_length=50)
    cname = models.CharField(max_length=100)
    milegae = models.IntegerField()
    seats = models.IntegerField()
    luggage = models.IntegerField()
    desc = models.TextField()
    air=models.BooleanField(default=True)
    gps=models.BooleanField(default=True)
    childseat=models.BooleanField(default=True)
    luggage=models.TextField(default=True)
    music=models.BooleanField(default=False)
    seatbelt=models.BooleanField(default=True)
    sleepingbed=models.BooleanField(default=False)
    water=models.BooleanField(default=False)
    bluetooth=models.BooleanField(default=True)
    onboardcomputer=models.BooleanField(default=False) 
    audioinput=models.BooleanField(default=True)
    longtermtips=models.BooleanField(default=True)
    carkit=models.BooleanField(default=True)
    remotecontrollocking=models.BooleanField(default=True)
    climatecontrol=models.BooleanField(default=True) 
    cprice = models.IntegerField(null=True, blank=True)
    cimage = models.ImageField(default="")      
    
class Review(models.Model):
    STAR_CHOICES=[
        (1,'1 Star'),
        (2,'2 Stars'),
        (3,'3 Stars'),
        (4,'4 Stars'),
        (5,'5 Stars')
    ]
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='car_reviews')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_reviews')
    review = models.TextField()
    rating = models.IntegerField(choices=STAR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.car.cname} ({self.rating} stars)"