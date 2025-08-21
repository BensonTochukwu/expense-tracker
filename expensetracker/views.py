
from datetime import timedelta
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tracker.models import CustomUser, Regusers, Expenses
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from calendar import month_name
from datetime import datetime, timedelta
from django.db.models.functions import ExtractYear
from django.db.models import F, ExpressionWrapper, DateField
User = get_user_model()


def BASE(request):
    return render(request, 'base.html')


@login_required(login_url='/')
def DASHBOARD(request):
    end_date = timezone.now()
    start_date_7_days_ago = end_date - timedelta(days=7)
    today = end_date.date()
    yesterday = today - timedelta(days=1)
    start_date_month = end_date - timedelta(days=end_date.day - 1)
    user_id = request.user.id

    # Filter expenses for the last seven days
    data_last_seven_days = Expenses.objects.filter(
        deuser_id__admin_id=user_id, dateofexpenses__range=(start_date_7_days_ago, end_date))

    # Aggregate the sum of costs for the last seven days
    data_amount_last_seven_days = data_last_seven_days.aggregate(Sum('cost'))[
        'cost__sum'] or 0

    # Filter expenses for yesterday
    data_yesterday = Expenses.objects.filter(
        deuser_id__admin_id=user_id, dateofexpenses=yesterday)

    # Aggregate the sum of costs for yesterday, default to 0 if no records found
    data_amount_yesterday = data_yesterday.aggregate(Sum('cost'))[
        'cost__sum'] or 0

    # Filter expenses for today
    data_today = Expenses.objects.filter(
        deuser_id__admin_id=user_id, dateofexpenses=today)

    # Aggregate the sum of costs for today, default to 0 if no records found
    data_amount_today = data_today.aggregate(Sum('cost'))['cost__sum'] or 0

    # Filter expenses for the current month
    data_current_month = Expenses.objects.filter(
        deuser_id__admin_id=user_id, dateofexpenses__range=(start_date_month, end_date))

    # Aggregate the sum of costs for the current month, default to 0 if no records found
    data_amount_current_month = data_current_month.aggregate(Sum('cost'))[
        'cost__sum'] or 0

    return render(request, 'dashboard.html', {
        'data_amount_last_seven_days': data_amount_last_seven_days,
        'data_amount_yesterday': data_amount_yesterday,
        'data_amount_today': data_amount_today,
        'data_amount_current_month': data_amount_current_month,
        'today': today,  # Include today in the context
    })


def SIGNUP(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        mobilenumber = request.POST.get('mobilenumber')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email is already Exist')
            return redirect('signup')

        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username is already Exist')
            return redirect('signup')

        else:
            user = CustomUser(first_name=first_name, last_name=last_name,
                              email=email, profile_pic=profile_pic, username=username)
            user.set_password(password)
            user.save()
            deuser = Regusers(
                admin=user,
                mobilenumber=mobilenumber,

            )
            deuser.save()
            messages.success(request, 'You are successfully registered')
            return redirect('signup')

    return render(request, 'signup.html')


def LOGIN(request):
    return render(request, 'login.html')


def doLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's authenticate method to verify credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If user is valid, log them in and redirect to dashboard
            login(request, user)
            return redirect('dashboard')
        else:
            # If authentication fails, show error message
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        # In case a GET request comes, redirect to login page
        messages.error(request, 'Invalid request method')
        return redirect('login')


def doLogout(request):
    logout(request)
    return redirect('login')


login_required(login_url='/')


def PROFILE(request):
    reguser = Regusers.objects.get(admin=request.user.id)
    context = {
        "reguser": reguser,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobilenumber = request.POST.get('mobilenumber')

        try:
            # Get the Regusers instance associated with the current user
            reguser = Regusers.objects.get(admin=request.user.id)

            # Update the CustomUser fields
            custom_user = reguser.admin
            custom_user.first_name = first_name
            custom_user.last_name = last_name

            if profile_pic is not None and profile_pic != "":
                custom_user.profile_pic = profile_pic  # Update profile picture if provided

            custom_user.save()

            # Update the mobilenumber field in Regusers model
            if mobilenumber is not None and mobilenumber != "":
                reguser.mobilenumber = mobilenumber  # Assign the new mobilenumber

            # Save the Regusers instance
            reguser.save()

            messages.success(
                request, "Your profile has been updated successfully")
            return redirect('profile')

        except Regusers.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('profile')

    return render(request, 'profile.html')


@login_required(login_url='/')
def CHANGE_PASSWORD(request):
    context = {}
    ch = User.objects.filter(id=request.user.id)

    if len(ch) > 0:
        data = User.objects.get(id=request.user.id)
        context["data"]: data
    if request.method == "POST":
        current = request.POST["cpwd"]
        new_pas = request.POST['npwd']
        user = User.objects.get(id=request.user.id)
        un = user.username
        check = user.check_password(current)
        if check == True:
            user.set_password(new_pas)
            user.save()
            messages.success(request, 'Password Change  Succeesfully!!!')
            user = User.objects.get(username=un)
            login(request, user)
        else:
            messages.success(request, 'Current Password wrong!!!')
            return redirect("change_password")
    return render(request, 'change-password.html')


@login_required(login_url='/')
def ADDEXPENSES(request):
    if request.method == "POST":
        deuserid = Regusers.objects.get(admin=request.user.id)
        doexp = request.POST.get('dateofexp')
        item = request.POST.get('item')
        cost = request.POST.get('cost')
        userexpenses = Expenses(deuser_id=deuserid,
                                dateofexpenses=doexp,
                                item=item,
                                cost=cost)
        userexpenses.save()
        messages.success(request, 'Expense details has been added')
        return redirect('add_expenses')

    return render(request, 'add_expenses.html')


@login_required(login_url='/')
def MANAGE_EXPENSES(request):
    deuser = Regusers.objects.filter(admin=request.user.id)
    print("deuser:", deuser)

    dailyexpenseuser_list = []  # Create an empty list to store dailyexpenseuser

    for i in deuser:
        deuserid = i.id
        dailyexpenseuser = Expenses.objects.filter(deuser_id=deuserid)
        # Add dailyexpenseuser to the list
        dailyexpenseuser_list.extend(dailyexpenseuser)

    context = {
        # Pass the list of dailyexpenseuser to the context
        'dailyexpenseuser': dailyexpenseuser_list,
    }

    return render(request, 'manage_expense.html', context)


def DELETE_EXPENSES(request, id):
    try:
        # Get the specific expense by ID
        expenses = Expenses.objects.get(id=id)
        expenses.delete()
        messages.success(request, 'Record Deleted Successfully!!!')
    except Expenses.DoesNotExist:
        messages.error(request, 'Expense not found.')

    # Redirect to the desired page after deletion, e.g., 'manage_expenses'
    # Change 'manage_expenses' to the actual name of the view you want to redirect to
    return redirect('manage_expense')


def data_between_dates(request, deuser_id):
    deuser = get_object_or_404(Regusers, admin=deuser_id)
    dailyexpenseuser_list = []

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Initialize query
    dailyexpenseuser = Expenses.objects.filter(deuser_id=deuser)

    if start_date and end_date:
        dailyexpenseuser = dailyexpenseuser.filter(
            dateofexpenses__range=(start_date, end_date))
        dailyexpenseuser_list.extend(dailyexpenseuser)

    context = {
        'dailyexpenseuser': dailyexpenseuser_list,
        'start_date': start_date,
        'end_date': end_date,
        'deuser_id': deuser_id,  # Pass deuser_id for form action URL
    }

    return render(request, 'data_between_dates.html', context)


def monthwise_report(request, deuser_id):
    deuser = get_object_or_404(Regusers, admin=deuser_id)
    dailyexpenseuser_list = []
    selected_month = request.GET.get('month', '')
    data1 = Expenses.objects.filter(deuser_id=deuser)

    if selected_month:
        data1 = Expenses.objects.filter(dateofexpenses__month=selected_month)
    dailyexpenseuser_list.extend(data1)

    total_amount1 = data1.aggregate(Sum('cost'))['cost__sum']
    month_name_selected = month_name[int(
        selected_month)] if selected_month else None

    context = {
        'selected_month': selected_month,
        'month_name_selected': month_name_selected,
        'data1': data1,
        'total_amount1': total_amount1,
        'data1': dailyexpenseuser_list,
    }

    return render(request, 'monthwise-expense.html', context)


def yearwise_report(request, deuser_id):
    deuser = get_object_or_404(Regusers, admin=deuser_id)
    selected_year = request.GET.get('year', '')

    # Get all expenses for the user
    data1 = Expenses.objects.filter(deuser_id=deuser)

    # Group by year and sum the costs for each year
    yearly_expenses = data1.annotate(year=ExtractYear('dateofexpenses')).values(
        'year').annotate(total_cost=Sum('cost')).order_by('-year')

    if selected_year:
        # Filter data by the selected year if provided
        data1 = yearly_expenses.filter(year=selected_year)
    else:
        data1 = yearly_expenses

    total_amount1 = data1.aggregate(Sum('total_cost'))['total_cost__sum']

    # Generate the range of years (from 2000 to current year)
    current_year = datetime.now().year
    start_year = 2000
    years_range = range(current_year, start_year - 1, -1)

    context = {
        'selected_year': selected_year,
        'data1': data1,
        'total_amount1': total_amount1,
        'years_range': years_range,
    }

    return render(request, 'yearwise-expense.html', context)
